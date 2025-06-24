package dto

type RegisterRequest struct {
	Username          string `json:"username"`
	Email             string `json:"email"`
	EncryptedPassword string `json:"password"`
	Vrfcode           string `json:"vrfcode"`
}

type RegisterResponse struct {
	Id       uint   `json:"id"`
	Username string `json:"username"`
}
