package dto

type ClubPostBasic struct {
	PostId       int    `json:"post_id"`
	ClubId       int    `json:"club_id"`
	AuthorId     int    `json:"author_id"`
	Title        string `json:"title"`
	IsPinned     bool   `json:"is_pinned"`
	CommentCount int    `json:"comment_count"`
	CreatedAt    string `json:"created_at"`
	ContentUrl   string `json:"content_url"`
}

type CreatePostRequest struct {
	ClubId  int    `json:"club_id"`
	Title   string `json:"title"`
	Content string `json:"content"`
}
