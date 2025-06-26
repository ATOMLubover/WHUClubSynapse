package repo

import (
	"log/slog"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type ClubPostRepo interface {
	AddPost(post dbstruct.ClubPost) error
	GetClubPostList(clubId int) ([]*dbstruct.ClubPost, error)
}

type sClubPostRepo struct {
	database *gorm.DB
	logger   *slog.Logger
}

func CreateClubPosRespo(
	database *gorm.DB,
	logger *slog.Logger,
) ClubPostRepo {
	return &sClubPostRepo{
		database: database,
		logger:   logger,
	}
}

func (r *sClubPostRepo) AddPost(post dbstruct.ClubPost) error {
	return r.database.Create(&post).Error
}

func (r *sClubPostRepo) GetClubPostList(clubId int) ([]*dbstruct.ClubPost, error) {
	var posts []*dbstruct.ClubPost
	err := r.database.Where("club_id = ?", clubId).Find(&posts).Error
	return posts, err
}
