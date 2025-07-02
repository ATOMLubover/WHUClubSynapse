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
	transaction := c.tx.Begin()
	defer func() {
		if r := recover(); r != nil {
			transaction.Rollback()
		}
	}()

	if err := transaction.WithContext(ctx).Transaction(handler); err != nil {
		transaction.Rollback()
		return err

	}

	return transaction.Commit().Error
}
