package repo

import (
	"log/slog"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type CatogoryRepo interface {
	AddCategory(cat *dbstruct.Category) error
	GetCategoryList() ([]*dbstruct.Category, error)
	GetCategoryInfo(id int) (*dbstruct.Category, error)
}

type sCategoryRepo struct {
	database *gorm.DB
	logger   *slog.Logger
}

func CreateCategoryRepo(
	database *gorm.DB,
	logger *slog.Logger,
) CatogoryRepo {
	return &sCategoryRepo{
		database: database,
		logger:   logger,
	}
}

func (r *sCategoryRepo) AddCategory(cat *dbstruct.Category) error {
	return r.database.Create(cat).Error
}

func (r *sCategoryRepo) GetCategoryList() ([]*dbstruct.Category, error) {
	var cats []*dbstruct.Category
	err := r.database.Find(&cats).Error
	return cats, err
}
func (r *sCategoryRepo) GetCategoryInfo(id int) (*dbstruct.Category, error) {
	var cat dbstruct.Category
	err := r.database.
		Where("category_id = ?", id).
		First(&cat).Error
	return &cat, err
}
