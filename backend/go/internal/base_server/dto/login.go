package dto

type LoginRequest struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

type LoginResponse struct {
	UserId     int    `json:"user_id"`
	Username   string `json:"username"`
	Email      string `json:"email"`
	AvatarUrl  string `json:"avatar_url"`
	Role       string `json:"role"`
	LastActive string `json:"last_active"`
}
