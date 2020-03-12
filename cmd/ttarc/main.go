package main

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
					Type                 string `json:"@type"`
					UserInteractionCount int64  `json:"userInteractionCount"`
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
				Type                 string `json:"@type"`
				UserInteractionCount int64  `json:"userInteractionCount"`
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

func main() {

}
