package config

import (
	"errors"
	"fmt"
	"path/filepath"

	"github.com/spf13/viper"
)

func LoadConfig[T any](cfg *T, relPath string) error {
	absPath, err := filepath.Abs(relPath)
	if err != nil {
		return errors.New("配置文件路径解析错误：" + err.Error())
	}

	fmt.Printf("配置文件绝对路径：%s\n", absPath)

	viper.SetConfigType("json")
	viper.SetConfigFile(absPath)

	if err := viper.ReadInConfig(); err != nil {
		return errors.New("读取配置文件失败")
	}

	if err := viper.Unmarshal(cfg); err != nil {
		return errors.New("配置反序列化失败")
	}

	return nil
}
