package dto

type ProcCreatePostRequest struct {
	CreatePostAppliId int    `json:"post_id"`
	Result            string `json:"result"`
	Reason            string `json:"reason"`
}
