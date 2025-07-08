package dto

type UpdateUserRequest struct {
	UserId    int    `json:"user_id"`
	Username  string `json:"username"`
	Password  string `json:"password"`
	Email     string `json:"email"`
	Extension string `json:"extension"` // 扩展字段，可以存储额外信息
}
