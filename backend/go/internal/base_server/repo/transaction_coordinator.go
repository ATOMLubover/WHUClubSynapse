package repo

import (
	"context"

	"gorm.io/gorm"
)

type TransactionCoordinator interface {
	RunInTransaction(ctx context.Context, handler func(tx *gorm.DB) error) error
}

type sTransactionCoordinator struct {
	tx *gorm.DB
}

func NewTransactionCoordinator(tx *gorm.DB) TransactionCoordinator {
	return &sTransactionCoordinator{
		tx: tx,
	}
}

func (c *sTransactionCoordinator) RunInTransaction(ctx context.Context, handler func(tx *gorm.DB) error) error {
	return c.tx.WithContext(ctx).Transaction(handler)
}
