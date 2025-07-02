package dbstruct

import (
	"time"

	"gorm.io/datatypes"
	"gorm.io/gorm"
)

type User struct {
	UserId       uint      `gorm:"primaryKey;column:user_id"`
	Username     string    `gorm:"size:50;unique;not null"`
	PasswordHash string    `gorm:"type:char(60);not null"`
	Email        string    `gorm:"size:100;unique;not null"`
	AvatarUrl    string    `gorm:"size:255"`
	Role         string    `gorm:"size:20;default:'user';not null"`
	CreatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	UpdatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	LastActive   time.Time
}

const (
	ROLE_USER      = "user"
	ROLE_PUBLISHER = "publisher"
	ROLE_ADMIN     = "admin"
)

func (User) TableName() string { return "users" }

type Category struct {
	CategoryId uint   `gorm:"primaryKey;column:category_id"`
	Name       string `gorm:"size:50;unique;not null"`
}

func (Category) TableName() string { return "categories" }

type Club struct {
	ClubId       uint           `gorm:"primaryKey;column:club_id" json:"club_id"`
	Name         string         `gorm:"size:100;not null" json:"name"`
	LeaderId     uint           `gorm:"not null" json:"leader_id"`
	CategoryId   uint           `gorm:"not null" json:"category_id"`
	Description  string         `gorm:"type:text;not null" json:"description"`
	LogoUrl      string         `gorm:"size:255" json:"logo_url"`
	MemberCount  int            `gorm:"default:0;not null" json:"member_count"`
	Requirements string         `gorm:"type:text" json:"requirements"`
	CreatedAt    time.Time      `gorm:"default:CURRENT_TIMESTAMP;not null" json:"created_at"`
	UpdatedAt    time.Time      `gorm:"default:CURRENT_TIMESTAMP;not null" json:"updated_at"`
	Tags         datatypes.JSON `json:"type:jsonb"`

	Leader   User     `gorm:"foreignKey:LeaderId" json:"-"`
	Category Category `gorm:"foreignKey:CategoryId" json:"-"`
}

func (Club) TableName() string { return "clubs" }

type ClubMember struct {
	MemberId   uint      `gorm:"primaryKey;column:member_id"`
	UserId     uint      `gorm:"not null"`
	ClubId     uint      `gorm:"not null"`
	RoleInClub string    `gorm:"size:20;default:'member';not null"`
	JoinedAt   time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	LastActive time.Time `gorm:"default:CURRENT_TIMESTAMP"`

	User *User `gorm:"foreignKey:UserId"`
	Club *Club `gorm:"foreignKey:ClubId"`
}

const (
	ROLE_CLUB_MEMBER = "member"
	ROLE_CLUB_LEADER = "leader"
)

func (ClubMember) TableName() string { return "club_members" }

type CreateClubAppli struct {
	CreateAppliId  uint           `gorm:"primaryKey;column:create_appli_id"`
	UserId         uint           `gorm:"not null"`
	Proposal       datatypes.JSON `gorm:"type:jsonb;not null"`
	AppliedAt      time.Time      `gorm:"default:CURRENT_TIMESTAMP;not null"`
	Status         string         `gorm:"size:20;default:'pending';not null"`
	RejectedReason string         `gorm:"size:255"`
	ReviewedAt     time.Time

	User User `gorm:"foreignKey:UserId"`
}

func (CreateClubAppli) TableName() string { return "create_club_applications" }

type JoinClubAppli struct {
	JoinAppliId    uint      `gorm:"primaryKey;column:join_appli_id"`
	UserId         uint      `gorm:"not null"`
	ClubId         uint      `gorm:"not null"`
	AppliedAt      time.Time `gorm:"default:CURRENT_TIMESTAMP;not null"`
	Status         string    `gorm:"size:20;default:'pending';not null"`
	RejectedReason string    `gorm:"size:255"`
	ApplyReason    string    `gorm:"type:text;not null"`
	ReviewedAt     time.Time

	User User `gorm:"foreignKey:UserId"`
	Club Club `gorm:"foreignKey:ClubId"`
}

func (JoinClubAppli) TableName() string { return "join_club_applications" }

type ClubFavorite struct {
	ClubFavoriteId uint `gorm:"primaryKey;column:club_favorite_id"`
	UserId         uint `gorm:"not null"`
	ClubId         uint `gorm:"not null"`
	CreatedAt      time.Time
	DeletedAt      gorm.DeletedAt `gorm:"index"`

	User User `gorm:"foreignKey:UserId"`
	Club Club `gorm:"foreignKey:ClubId"`
}

func (ClubFavorite) TableName() string { return "club_favorites" }

type ClubPost struct {
	PostId       uint      `gorm:"primaryKey;column:post_id" json:"post_id"`
	ClubId       uint      `gorm:"not null" json:"club_id"`
	UserId       uint      `gorm:"not null" json:"user_id"`
	Title        string    `gorm:"size:120;not null" json:"title"`
	ContentUrl   string    `gorm:"type:text;not null" json:"content_url"`
	Visibility   int16     `gorm:"default:0;not null" json:"visibility"` // 0=公开, 1=社团成员, 2=管理员
	IsPinned     bool      `gorm:"default:false;not null" json:"is_pinned"`
	CommentCount int       `gorm:"default:0;not null" json:"comment_count"`
	CreatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null" json:"created_at"`
	UpdatedAt    time.Time `gorm:"default:CURRENT_TIMESTAMP;not null" json:"updated_at"`

	Club   Club `gorm:"foreignKey:ClubId" json:"-"`
	Author User `gorm:"foreignKey:UserId" json:"-"`
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

type UpdateClubInfoAppli struct {
	UpdateAppliId  uint           `gorm:"primaryKey;column:update_appli_id"`
	ClubId         uint           `gorm:"not null"`
	ApplicantId    uint           `gorm:"not null"`
	Proposal       datatypes.JSON `gorm:"type:jsonb;not null"`
	Reason         string         `gorm:"type:text;not null"`
	AppliedAt      time.Time      `gorm:"default:CURRENT_TIMESTAMP;not null"`
	Status         string         `gorm:"size:20;default:'pending';not null"`
	ReviewedAt     time.Time
	RejectedReason string `gorm:"size:255"`

	Club      Club `gorm:"foreignKey:ClubId"`
	Applicant User `gorm:"foreignKey:ApplicantId"`
}

func (UpdateClubInfoAppli) TableName() string { return "update_club_info_applications" }

// type CreatePostAppli struct {
// 	PostAppliId     uint           `gorm:"primaryKey;column:post_appli_id"`
// 	ClubId          uint           `gorm:"not null"`
// 	ApplicantId     uint           `gorm:"not null"`
// 	Proposal        datatypes.JSON `gorm:"type:jsonb;not null"`
// 	DraftContentUrl string         `gorm:"size:255;not null"`
// 	AppliedAt       time.Time      `gorm:"default:CURRENT_TIMESTAMP;not null"`
// 	Status          string         `gorm:"size:20;default:'pending';not null"`
// 	ReviewedAt      time.Time
// 	RejectedReason  string `gorm:"size:255"`

// 	Club      Club `gorm:"foreignKey:ClubId"`
// 	Applicant User `gorm:"foreignKey:ApplicantId"`
// }

// func (CreatePostAppli) TableName() string { return "create_post_applications" }
