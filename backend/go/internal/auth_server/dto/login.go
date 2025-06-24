package dto

type LoginRequest struct {
	Username          string `json:"username"`
	EncryptedPassword string `json:"password"`
}

type LoginResponse struct {
	Username   string `json:"username"`
	Email      string `json:"email"`
	AvatarUrl  string `json:"avatar_url"`
	Role       string `json:"role"`
	LastActive string `json:"last_active"`
}
