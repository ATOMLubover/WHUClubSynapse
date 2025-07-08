package jwtutil

import (
	"errors"
	"net/http"

	"github.com/google/go-cmp/cmp"
)

func ValiadateToken[T any](
	tokenStr string,
	expected T,
	factory *CliamsFactory[T],
) (int, error) {
	claims, err := factory.ParseToken(tokenStr)
	if err != nil {
		return http.StatusUnauthorized, err
	}

	if !cmp.Equal(expected, claims) {
		return http.StatusForbidden, errors.New("解析值不为expected")
	}

	return http.StatusOK, nil
}
