package dbstruct

import (
	"time"
)

type User struct {
	UserId       uint      `gorm:"primaryKey;column:user_id"`
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
	CategoryId uint   `gorm:"primaryKey;column:category_id"`
	Name       string `gorm:"size:50;unique;not null"`
}

func (Category) TableName() string { return "categories" }

type Club struct {
	ClubId       uint      `gorm:"primaryKey;column:club_id"`
	Name         string    `gorm:"size:100;not null"`
	LeaderId     uint      `gorm:"not null"`
	CategoryId   uint      `gorm:"not null"`
	Description  string    `gorm:"type:text;not null"`
	LogoUrl      string    `gorm:"size:255"`
	MemberCount  int       `gorm:"default:0;not null"`
	Status       string    `gorm:"size:20;default:'pending';not null"`
	Requirements string    `gorm:"type:text"`
	CreatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	UpdatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	ApprovedAt   time.Time

	Leader   User     `gorm:"foreignKey:LeaderId"`
	Category Category `gorm:"foreignKey:CategoryId"`
}

func (Club) TableName() string { return "clubs" }

type ClubMember struct {
	MemberId   uint      `gorm:"primaryKey;column:member_id"`
	UserId     uint      `gorm:"not null"`
	ClubId     uint      `gorm:"not null"`
	RoleInClub string    `gorm:"size:20;default:'member';not null"`
	JoinedAt   time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	LastActive time.Time `gorm:"default:CURRENT_TIMESTAMP"`

	User User `gorm:"foreignKey:UserId"`
	Club Club `gorm:"foreignKey:ClubId"`
}

func (ClubMember) TableName() string { return "club_members" }

type CreateClubApplication struct {
	CreateAppliId  uint      `gorm:"primaryKey;column:join_appli_id"`
	UserId         uint      `gorm:"not null"`
	AppliedAt      time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	Status         string    `gorm:"size:20;default:'pending';not null"`
	RejectedReason string    `gorm:"size:255"`
	ReviewedAt     time.Time

	User User `gorm:"foreignKey:UserId"`
}

func (CreateClubApplication) TableName() string { return "create_club_application" }

type JoinClubApplication struct {
	JoinAppliId    uint      `gorm:"primaryKey;column:join_appli_id"`
	UserId         uint      `gorm:"not null"`
	ClubId         uint      `gorm:"not null"`
	AppliedAt      time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	Status         string    `gorm:"size:20;default:'pending';not null"`
	RejectedReason string    `gorm:"size:255"`
	ReviewedAt     time.Time

	User User `gorm:"foreignKey:UserId"`
	Club Club `gorm:"foreignKey:ClubId"`
}

func (JoinClubApplication) TableName() string { return "join_club_applications" }

type Favorite struct {
	FavoriteId uint `gorm:"primaryKey;column:favorite_id"`
	UserId     uint `gorm:"not null"`
	ClubId     uint `gorm:"not null"`

	User User `gorm:"foreignKey:UserId"`
	Club Club `gorm:"foreignKey:ClubId"`
}

func (Favorite) TableName() string { return "favorites" }

type ClubPost struct {
	PostId       uint      `gorm:"primaryKey;column:post_id"`
	ClubId       uint      `gorm:"not null"`
	UserId       uint      `gorm:"not null"`
	Title        string    `gorm:"size:120;not null"`
	ContentUrl   string    `gorm:"type:text;not null"`
	Visibility   int16     `gorm:"default:0;not null"` // 0=公开, 1=社团成员, 2=管理员
	IsPinned     bool      `gorm:"default:false;not null"`
	CommentCount int       `gorm:"default:0;not null"`
	CreatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	UpdatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`

	Club     Club `gorm:"foreignKey:ClubId"`
	Author   User `gorm:"foreignKey:UserId"`
	Comments []ClubPostComment
}

func (ClubPost) TableName() string { return "club_posts" }

type ClubPostComment struct {
	CommentId uint      `gorm:"primaryKey;column:comment_id"`
	PostId    uint      `gorm:"not null"`
	UserId    uint      `gorm:"not null"`
	Content   string    `gorm:"type:text;not null"`
	CreatedAt time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`

	Post   ClubPost `gorm:"foreignKey:PostId"`
	Author User     `gorm:"foreignKey:UserId"`
}

func (ClubPostComment) TableName() string { return "club_post_comments" }
