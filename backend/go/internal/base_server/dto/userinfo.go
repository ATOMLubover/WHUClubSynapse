package dto

type UserInfo struct {
	UserId     uint   `json:"user_id"`
	Username   string `json:"username"`
	Email      string `json:"email"`
	AvatarUrl  string `json:"avatar_url"`
	Role       string `json:"role"`
	LastActive string `json:"last_active"`
	Extension  string `json:"extension"` // 扩展字段，可以存储额外信息

	CreatedAt string `json:"created_at"` // 创建时间
	UpdatedAt string `json:"updated_at"` // 更新时间
}
