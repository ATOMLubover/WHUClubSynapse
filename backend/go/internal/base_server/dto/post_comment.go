package dto

type PostComment struct {
	CommentId int    `json:"comment_id"`
	UserId    int    `json:"user_id"`
	PostId    int    `json:"post_id"`
	Content   string `json:"content"`
	CreatedAt string `json:"created_at"`
}
