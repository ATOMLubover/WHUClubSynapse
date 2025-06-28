package jsonbutil

import (
	"encoding/json"
	"errors"

	"gorm.io/datatypes"
)

func ToJsonb(obj interface{}) (datatypes.JSON, error) {
	if obj == nil {
		return nil, errors.New("cannot convert nil to JSONB")
	}

	bytes, err := json.Marshal(obj)
	if err != nil {
		return nil, err
	}
	return datatypes.JSON(bytes), nil
}

func FromJsonb(jsonData datatypes.JSON, dest interface{}) error {
	return json.Unmarshal([]byte(jsonData), dest)
}
