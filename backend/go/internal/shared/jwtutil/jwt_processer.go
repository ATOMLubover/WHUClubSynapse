package jwtutil

import (
	"errors"
	"log/slog"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type sCustomClaims[T any] struct {
	jwt.RegisteredClaims

	Inner T
}

type CliamsFactory[T any] struct {
	ExpirationTime time.Duration
	SecretKey      string

	logger *slog.Logger
}

func NewClaimsFactory[ClaimItem any](
	expiration time.Duration,
	secretKey string,
	logger *slog.Logger,
) *CliamsFactory[ClaimItem] {
	logger.Info("ClaimsFactory建立", "expiration", expiration)

	return &CliamsFactory[ClaimItem]{
		ExpirationTime: expiration,
		SecretKey:      secretKey,
		logger:         logger,
	}
}

func (f *CliamsFactory[T]) GenToken(item T) (string, error) {
	now := time.Now()
	expireAt := now.Add(f.ExpirationTime)

	f.logger.Info("ClaimsFactory生成token", "now", now, "expire_at", expireAt)

	claims := sCustomClaims[T]{
		Inner: item,
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(expireAt),
			IssuedAt:  jwt.NewNumericDate(now),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	signed, err := token.SignedString([]byte(f.SecretKey))

	return signed, err
}

func (f *CliamsFactory[T]) ParseToken(signed string) (*T, error) {
	token, err := jwt.ParseWithClaims(
		signed,
		&sCustomClaims[T]{},
		func(token *jwt.Token) (any, error) {
			return []byte(f.SecretKey), nil
		},
	)
	if err != nil {
		return nil, err
	}

	claims, ok := token.Claims.(*sCustomClaims[T])
	if !ok || !token.Valid {
		return nil, errors.New("token无法解析")
	}

	return &claims.Inner, err
}
