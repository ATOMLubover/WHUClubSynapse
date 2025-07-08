//package repo

// import (
// 	"errors"
// 	"log/slog"
// 	"whuclubsynapse-server/internal/shared/dbstruct"

// 	"gorm.io/gorm"
// 	"gorm.io/gorm/clause"
// )

// type CreatePostAppliRepo interface {
// 	AddCreatePostAppli(appli *dbstruct.CreatePostAppli) error
// 	GetCreatePostAppliList(clubId int) ([]*dbstruct.CreatePostAppli, error)
// 	GetApplisByUserId(userId int) ([]*dbstruct.CreatePostAppli, error)
// 	GetAppliForUpdate(tx *gorm.DB, appliId int) (*dbstruct.CreatePostAppli, error)
// 	ApproveAppli(tx *gorm.DB, appliId int) error
// 	RejectAppli(appliId int, reason string) error
// }

// type sCreatePostAppliRepo struct {
// 	database *gorm.DB
// 	logger   *slog.Logger
// }

// func CreateCreatePostAppliRepo(
// 	database *gorm.DB,
// 	logger *slog.Logger,
// ) CreatePostAppliRepo {
// 	return &sCreatePostAppliRepo{
// 		database: database,
// 		logger:   logger,
// 	}
// }

// func (r *sCreatePostAppliRepo) AddCreatePostAppli(appli *dbstruct.CreatePostAppli) error {
// 	return r.database.Create(appli).Error
// }

// func (r *sCreatePostAppliRepo) GetCreatePostAppliList(clubId int) ([]*dbstruct.CreatePostAppli, error) {
// 	var applis []*dbstruct.CreatePostAppli
// 	err := r.database.
// 		Where("club_id = ?", clubId).
// 		Find(&applis).Error
// 	return applis, err
// }

// func (r *sCreatePostAppliRepo) GetApplisByUserId(userId int) ([]*dbstruct.CreatePostAppli, error) {
// 	var applis []*dbstruct.CreatePostAppli
// 	err := r.database.
// 		Where("user_id = ?", userId).
// 		Find(&applis).Error
// 	return applis, err
// }

// func (r *sCreatePostAppliRepo) GetAppliForUpdate(tx *gorm.DB, appliId int) (*dbstruct.CreatePostAppli, error) {
// 	if appliId <= 0 {
// 		return nil, errors.New("无效参数")
// 	}

// 	var appli dbstruct.CreatePostAppli
// 	err := tx.
// 		Model(&dbstruct.CreatePostAppli{}).
// 		Clauses(clause.Locking{Strength: "UPDATE"}).
// 		Where("post_appli_id = ?", appliId).
// 		First(&appli).Error

// 	return &appli, err
// }
// func (r *sCreatePostAppliRepo) ApproveAppli(tx *gorm.DB, appliId int) error {
// 	if appliId <= 0 {
// 		return errors.New("无效参数")
// 	}

// 	return tx.
// 		Model(&dbstruct.CreatePostAppli{}).
// 		Where("post_appli_id = ?", appliId).
// 		Update("status", "approved").Error
// }

// func (r *sCreatePostAppliRepo) RejectAppli(appliId int, reason string) error {
// 	if appliId <= 0 {
// 		return errors.New("无效参数")
// 	}

// 	return r.database.
// 		Model(&dbstruct.CreatePostAppli{}).
// 		Where("post_appli_id = ?", appliId).
// 		Select("status", "reason").
// 		Updates(dbstruct.CreatePostAppli{
// 			Status:         "rejected",
// 			RejectedReason: reason,
// 		}).Error
// }
