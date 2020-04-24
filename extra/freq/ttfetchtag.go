package main

import (
	"bufio"
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path"
	"strings"
	"time"

	"github.com/adrg/xdg"
	"github.com/gosimple/slug"
	"github.com/sethgrid/pester"
)

var (
	cacheDir   = flag.String("cache", path.Join(xdg.CacheHome, "ttfetchtag", time.Now().Format("20060102")), "cache directory")
	words      = flag.String("words", "words.txt", "word file")
	bestEffort = flag.Bool("b", false, "best effort")
	sleep      = flag.Duration("s", 2*time.Second, "sleep between requests")
	userAgent  = flag.String("ua", DefaultUserAgent, "user agent")

	Prefix           = "https://www.tiktok.com/node/share/tag"
	DefaultUserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
)

// readLines reads trimmers lines into a slice.
func ReadLines(r io.Reader) (lines []string, err error) {
	br := bufio.NewReader(r)
	for {
		line, err := br.ReadString('\n')
		if err == io.EOF {
			break
		}
		if err != nil {
			return nil, err
		}
		lines = append(lines, strings.TrimSpace(line))
	}
	return
}

func WriteFileReader(filename string, r io.Reader, perm os.FileMode) error {
	b, err := ioutil.ReadAll(r)
	if err != nil {
		return err
	}
	return WriteFile(filename, b, perm)
}

// WriteFile writes the data to a temp file and atomically move if everything else succeeds.
func WriteFile(filename string, data []byte, perm os.FileMode) error {
	dir, name := path.Split(filename)
	f, err := ioutil.TempFile(dir, name)
	if err != nil {
		return err
	}
	_, err = f.Write(data)
	if err == nil {
		err = f.Sync()
	}
	if closeErr := f.Close(); err == nil {
		err = closeErr
	}
	if permErr := os.Chmod(f.Name(), perm); err == nil {
		err = permErr
	}
	if err == nil {
		err = os.Rename(f.Name(), filename)
	}
	// Any err should result in full cleanup.
	if err != nil {
		os.Remove(f.Name())
	}
	return err
}

// FetchLink fetches a link and writes it atomically into a file.
func FetchLink(link, filename string) error {
	client := pester.New()
	client.SetRetryOnHTTP429(true)
	client.Backoff = pester.ExponentialBackoff
	req, err := http.NewRequest("GET", link, nil)
	if err != nil {
		return err
	}
	req.Header.Set("User-Agent", *userAgent)
	resp, err := client.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return WriteFileReader(filename, resp.Body, 0755)
}

func main() {
	flag.Parse()

	if _, err := os.Stat(*cacheDir); os.IsNotExist(err) {
		if err := os.MkdirAll(*cacheDir, 0755); err != nil {
			log.Fatal(err)
		}
	}

	f, err := os.Open(*words)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()
	words, err := ReadLines(f)
	if err != nil {
		log.Fatal(err)
	}
	for _, w := range words {
		dst := path.Join(*cacheDir, slug.Make(w))
		if fi, err := os.Stat(dst); err == nil && fi.Size() > 0 {
			log.Printf("already cached: %s", dst)
			continue
		}
		link := fmt.Sprintf("%s/%s", Prefix, w)
		if err := FetchLink(link, dst); err != nil {
			if *bestEffort {
				log.Printf("fetch failed: %s %s", err, link)
			} else {
				log.Fatal(err)
			}
		}
		log.Printf("done: %s %s", link, dst)
		time.Sleep(*sleep)
	}
}
