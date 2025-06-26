package dto

type ClubPostBasic struct {
	PostId       int    `json:"post_id"`
	ClubId       int    `json:"club_id"`
	AuthorId    int    `json:"author_id"`
	Title        string `json:"title"`
	CommentCount int    `json:"comment_count"`
	CreatedAt    string `json:"created_at"`
}

type ClubPost struct {
	ClubPostBasic
	ContentUrl string `json:"content_url"`
}
