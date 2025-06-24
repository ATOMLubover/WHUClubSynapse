package model

import (
	"time"
)

type User struct {
	UserID       uint      `gorm:"primaryKey;column:user_id"`
	Username     string    `gorm:"size:50;unique;not null"`
	PasswordHash string    `gorm:"type:char(60);not null"`
	Email        string    `gorm:"size:100;unique;not null"`
	AvatarURL    string    `gorm:"size:255"`
	Role         string    `gorm:"size:20;default:'user';not null"`
	CreatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	UpdatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	LastActive   time.Time
}

func (User) TableName() string { return "users" }

type Category struct {
	CategoryID uint   `gorm:"primaryKey;column:category_id"`
	Name       string `gorm:"size:50;unique;not null"`
}

func (Category) TableName() string { return "categories" }

type Club struct {
	ClubID       uint      `gorm:"primaryKey;column:club_id"`
	Name         string    `gorm:"size:100;not null"`
	LeaderID     uint      `gorm:"not null"`
	CategoryID   uint      `gorm:"not null"`
	Description  string    `gorm:"type:text;not null"`
	LogoURL      string    `gorm:"size:255"`
	MemberCount  int       `gorm:"default:0;not null"`
	Status       string    `gorm:"size:20;default:'pending';not null"`
	Requirements string    `gorm:"type:text"`
	CreatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	UpdatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	ApprovedAt   time.Time

	Leader   User     `gorm:"foreignKey:LeaderID"`
	Category Category `gorm:"foreignKey:CategoryID"`
}

func (Club) TableName() string { return "clubs" }

type ClubMember struct {
	MemberID   uint      `gorm:"primaryKey;column:member_id"`
	UserID     uint      `gorm:"not null"`
	ClubID     uint      `gorm:"not null"`
	RoleInClub string    `gorm:"size:20;default:'member';not null"`
	JoinedAt   time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	LastActive time.Time `gorm:"default:CURRENT_TIMESTAMP"`

	User User `gorm:"foreignKey:UserID"`
	Club Club `gorm:"foreignKey:ClubID"`
}

func (ClubMember) TableName() string { return "club_members" }

type CreateClubApplication struct {
	JoinAppliID    uint      `gorm:"primaryKey;column:join_appli_id"`
	UserID         uint      `gorm:"not null"`
	AppliedAt      time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	Status         string    `gorm:"size:20;default:'pending';not null"`
	RejectedReason string    `gorm:"size:255"`
	ReviewedAt     time.Time

	User User `gorm:"foreignKey:UserID"`
}

func (CreateClubApplication) TableName() string { return "create_club_application" }

type JoinClubApplication struct {
	JoinAppliID    uint      `gorm:"primaryKey;column:join_appli_id"`
	UserID         uint      `gorm:"not null"`
	ClubID         uint      `gorm:"not null"`
	AppliedAt      time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	Status         string    `gorm:"size:20;default:'pending';not null"`
	RejectedReason string    `gorm:"size:255"`
	ReviewedAt     time.Time

	User User `gorm:"foreignKey:UserID"`
	Club Club `gorm:"foreignKey:ClubID"`
}

func (JoinClubApplication) TableName() string { return "join_club_applications" }

type Favorite struct {
	FavoriteID uint `gorm:"primaryKey;column:favorite_id"`
	UserID     uint `gorm:"not null"`
	ClubID     uint `gorm:"not null"`

	User User `gorm:"foreignKey:UserID"`
	Club Club `gorm:"foreignKey:ClubID"`
}

func (Favorite) TableName() string { return "favorites" }

type ClubPost struct {
	PostID       uint      `gorm:"primaryKey;column:post_id"`
	ClubID       uint      `gorm:"not null"`
	UserID       uint      `gorm:"not null"`
	Title        string    `gorm:"size:120;not null"`
	Content      string    `gorm:"type:text;not null"`
	Visibility   int16     `gorm:"default:0;not null"` // 0=公开, 1=社团成员, 2=管理员
	IsPinned     bool      `gorm:"default:false;not null"`
	CommentCount int       `gorm:"default:0;not null"`
	CreatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	UpdatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`

	Club     Club `gorm:"foreignKey:ClubID"`
	Author   User `gorm:"foreignKey:UserID"`
	Comments []ClubPostComment
}

func (ClubPost) TableName() string { return "club_posts" }

type ClubPostComment struct {
	CommentID uint      `gorm:"primaryKey;column:comment_id"`
	PostID    uint      `gorm:"not null"`
	UserID    uint      `gorm:"not null"`
	Content   string    `gorm:"type:text;not null"`
	CreatedAt time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`

	Post   ClubPost `gorm:"foreignKey:PostID"`
	Author User     `gorm:"foreignKey:UserID"`
}

func (ClubPostComment) TableName() string { return "club_post_comments" }
