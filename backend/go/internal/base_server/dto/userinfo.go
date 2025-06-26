package dto

type UserInfo struct {
	UserId     uint   `json:"user_id"`
	Username   string `json:"username"`
	Email      string `json:"email"`
	AvatarUrl  string `json:"avatar_url"`
	Role       string `json:"role"`
	LastActive string `json:"last_active"`
}
