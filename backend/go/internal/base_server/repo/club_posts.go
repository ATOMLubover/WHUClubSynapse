package repo

import (
	"errors"
	"log/slog"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type ClubPostRepo interface {
	AddPost(post *dbstruct.ClubPost) error
	ChangePostVisibility(postId, visibility int) error

	GetClubPostList(clubId, offset, num, visibility int) ([]*dbstruct.ClubPost, error)
	GetPinnedPost(clubId int) (*dbstruct.ClubPost, error)
	PinPost(postId int) error

	GetPostsByUserId(userId int) ([]*dbstruct.ClubPost, error)

	UpdatePostUrl(postId int, url string) error
}

type sClubPostRepo struct {
	database *gorm.DB
	logger   *slog.Logger
}

func CreateClubPostRepo(
	database *gorm.DB,
	logger *slog.Logger,
) ClubPostRepo {
	return &sClubPostRepo{
		database: database,
		logger:   logger,
	}
}

func (r *sClubPostRepo) AddPost(post *dbstruct.ClubPost) error {
	return r.database.Create(post).Error
}

func (r *sClubPostRepo) GetClubPostList(clubId, offset, num, visibility int) ([]*dbstruct.ClubPost, error) {
	var posts []*dbstruct.ClubPost
	err := r.database.
		Model(&dbstruct.ClubPost{}).
		Where("club_id = ? AND visibility <= ?", clubId, visibility).
		Order("created_at DESC").
		Offset(offset).
		Limit(num).
		Find(&posts).Error

	if err != nil && !errors.Is(err, gorm.ErrRecordNotFound) {
		return nil, err
	}

	return posts, nil
}

func (r *sClubPostRepo) ChangePostVisibility(postId, visibility int) error {
	return r.database.
		Model(&dbstruct.ClubPost{}).
		Where("post_id = ?", postId).
		Update("visibility", visibility).Error
}

func (r *sClubPostRepo) GetPinnedPost(clubId int) (*dbstruct.ClubPost, error) {
	var post dbstruct.ClubPost
	err := r.database.
		Where("club_id = ? AND is_pinned = ?", clubId, true).
		First(&post).Error

	if !errors.Is(err, gorm.ErrRecordNotFound) {
		return nil, err
	}

	return &post, nil
}

func (r *sClubPostRepo) PinPost(postId int) error {
	return r.database.Transaction(func(ctx *gorm.DB) error {
		if err := ctx.
			Model(&dbstruct.ClubPost{}).
			Where("is_pinned = ?", true).
			Update("is_pinned", false).Error; err != nil {
			return err
		}

		if err := ctx.
			Model(&dbstruct.ClubPost{}).
			Where("post_id = ?", postId).
			Update("is_pinned", true).Error; err != nil {
			return err
		}

		return nil
	})
}

func (r *sClubPostRepo) GetPostsByUserId(userId int) ([]*dbstruct.ClubPost, error) {
	var posts []*dbstruct.ClubPost
	err := r.database.
		Where("user_id = ?", userId).
		Find(&posts).Error
	return posts, err
}

func (r *sClubPostRepo) UpdatePostUrl(postId int, url string) error {
	err := r.database.
		Model(&dbstruct.ClubPost{}).
		Where("post_id = ?", postId).
		Update("content_url", url).Error
	if err != nil {
		return err
	}

	// if r.database.RowsAffected == 0 {
	// 	return errors.New("无法修改不存在的post")
	// }

	return nil
}
