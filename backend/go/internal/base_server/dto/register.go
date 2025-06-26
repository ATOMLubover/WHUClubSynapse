package dto

type RegisterRequest struct {
	Username          string `json:"username"`
	Email             string `json:"email"`
	EncryptedPassword string `json:"password"`
	Vrfcode           string `json:"vrfcode"`
}

type RegisterResponse struct {
	UserId   uint   `json:"user_id"`
	Username string `json:"username"`
}
