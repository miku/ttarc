// A simple tool that will use wget to download TikTok trending videos (only)
// and save them into WARC files with structured names.
package main

import (
	"bytes"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/exec"
	"time"

	"github.com/sethgrid/pester"
)

var (
	directoryPrefix = flag.String("P", ".", "output directory")
	warcName        = flag.String("f", fmt.Sprintf("ttarc-trending-%s", time.Now().Format("20060102150405")), "basename for warc file")
	userAgent       = flag.String("ua", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36", "user agent")
	verbose         = flag.Bool("verbose", false, "be verbose")
	bestEffort      = flag.Bool("b", false, "ignore wget errors, just log them")
	logFile         = flag.String("log", "", "log to stdout, if empty")
	showVersion     = flag.Bool("version", false, "show version and exit")

	Version   = "0.1.0"
	Commit    = ""
	Buildtime = ""
)

func main() {
	flag.Parse()

	if *showVersion {
		fmt.Printf("ttarc %s %s %s\n", Version, Commit, Buildtime)
		os.Exit(0)
	}

	if *logFile != "" {
		f, err := os.OpenFile(*logFile, os.O_CREATE|os.O_APPEND|os.O_WRONLY, 0644)
		if err != nil {
			log.Fatal(err)
		}
		defer f.Close()
		log.SetOutput(f)
	}

	trending := "https://m.tiktok.com/node/share/trending"
	req, err := http.NewRequest("GET", trending, nil)
	if err != nil {
		log.Fatal(err)
	}
	req.Header.Set("User-Agent", *userAgent)
	resp, err := pester.Do(req)
	if err != nil {
		log.Fatal(err)
	}
	defer resp.Body.Close()

	var (
		buf     bytes.Buffer
		payload Trending
	)
	r := io.TeeReader(resp.Body, &buf)
	dec := json.NewDecoder(r)
	if err := dec.Decode(&payload); err != nil {
		log.Fatal(err)
	}

	f, err := ioutil.TempFile("", "ttarc-tmp-")
	if err != nil {
		log.Fatal(err)
	}
	defer func() {
		f.Close()
		os.Remove(f.Name())
	}()
	if _, err := fmt.Fprintln(f, trending); err != nil {
		log.Fatal(err)
	}
	for _, item := range payload.Body.ItemList {
		if _, err := fmt.Fprintln(f, item.ContentUrl); err != nil {
			log.Fatal(err)
		}
	}
	opts := []string{
		"-O", "/dev/null",
		"--directory-prefix", *directoryPrefix,
		"--waitretry", "60",
		"--random-wait",
		"--warc-file", *warcName,
		"--warc-cdx", *warcName,
		"--warc-header", fmt.Sprintf("generator: ttarc %s %s %s", Version, Commit, Buildtime),
		"--input-file", f.Name(),
	}
	if *logFile != "" {
		opts = append(opts, []string{"-o", *logFile}...)
	}
	cmd := exec.Command("wget", opts...)
	if *verbose {
		log.Println(cmd)
	}
	b, err := cmd.CombinedOutput()
	if err != nil {
		if *bestEffort {
			log.Println(err)
		} else {
			log.Fatal(err)
		}
	}
	if *verbose {
		log.Println(string(b))
	}
}

// Trending was generated via https://github.com/bemasher/JSONGen from
// https://m.tiktok.com/node/share/trending.
type Trending struct {
	Body struct {
		ItemList []struct {
			Audio struct {
				Author           string `json:"author"`
				MainEntityOfPage struct {
					Id   string `json:"@id"`
					Type string `json:"@type"`
				} `json:"mainEntityOfPage"`
				Name string `json:"name"`
			} `json:"audio"`
			CommentCount string `json:"commentCount"`
			ContentUrl   string `json:"contentUrl"`
			Creator      struct {
				InteractionStatistic []struct {
					InteractionType struct {
						Type string `json:"@type"`
					} `json:"interactionType"`
					Type                 string      `json:"@type"`
					UserInteractionCount interface{} `json:"userInteractionCount"`
				} `json:"interactionStatistic"`
				Name string `json:"name"`
				Type string `json:"@type"`
				Url  string `json:"url"`
			} `json:"creator"`
			Description          string `json:"description"`
			Duration             string `json:"duration"`
			EmbedUrl             string `json:"embedUrl"`
			Height               int64  `json:"height"`
			InteractionStatistic []struct {
				InteractionType struct {
					Type string `json:"@type"`
				} `json:"interactionType"`
				Type                 string      `json:"@type"`
				UserInteractionCount interface{} `json:"userInteractionCount"`
			} `json:"interactionStatistic"`
			Keywords     string   `json:"keywords"`
			Name         string   `json:"name"`
			ThumbnailUrl []string `json:"thumbnailUrl"`
			UploadDate   string   `json:"uploadDate"`
			Url          string   `json:"url"`
			Width        int64    `json:"width"`
		} `json:"itemList"`
	} `json:"body"`
	ErrMsg     string `json:"errMsg"`
	StatusCode int64  `json:"statusCode"`
}
