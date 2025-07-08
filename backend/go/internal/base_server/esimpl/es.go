package esimpl

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"log"
	"strings"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"github.com/elastic/go-elasticsearch/v9"
	"github.com/elastic/go-elasticsearch/v9/esapi" // 确保导入这个包
)

var esClient *elasticsearch.Client

type Club dbstruct.Club

// 初始化ES客户端
func InitElasticsearch() error {
	cfg := elasticsearch.Config{
		Addresses: []string{"http://localhost:9200"},
	}
	client, err := elasticsearch.NewClient(cfg)
	if err != nil {
		return fmt.Errorf("创建ES客户端失败: %s", err)
	}
	esClient = client
	return nil
}

// 创建Club索引 - 严格使用文档中的函数
func CreateClubIndex() {
	// 1. 定义映射JSON（如文档示例）
	mapping := `{
		"mappings": {
			"properties": {
				"name": {"type": "text", "analyzer": "ik_max_word"},
				"desc": {"type": "text", "analyzer": "ik_max_word"},
				"tags": {"type": "keyword"}
			}
		}
	}`

	// 2. 创建索引请求 - 完全按照文档中的调用方式
	req := esapi.IndicesCreateRequest{
		Index: "clubs",
		Body:  strings.NewReader(mapping),
	}

	// 3. 执行请求
	res, err := req.Do(context.Background(), esClient)
	if err != nil {
		log.Fatalf("索引创建失败: %s", err)
	}
	defer res.Body.Close()

	if res.IsError() {
		log.Printf("ES错误响应: %s", res.String())
	} else {
		log.Println("Club索引创建成功")
	}
}

// 添加Club文档 - 严格使用文档中的函数
func AddClubToIndex(club Club) error {
	// 序列化文档
	data, err := json.Marshal(club)
	if err != nil {
		return err
	}

	// 创建索引请求 - 按照文档中的API调用
	req := esapi.IndexRequest{
		Index: "clubs",
		Body:  bytes.NewReader(data),
	}

	// 执行请求
	res, err := req.Do(context.Background(), esClient)
	if err != nil {
		return err
	}
	defer res.Body.Close()

	if res.IsError() {
		return fmt.Errorf("文档添加失败: %s", res.String())
	}

	return nil
}

// 搜索Clubs - 严格使用文档中的函数
func SearchClubs(query string) ([]Club, error) {
	// 构建查询
	searchQuery := `{
		"query": {
			"multi_match": {
				"query": "` + query + `",
				"fields": ["name", "desc"]
			}
		}
	}`

	// 创建搜索请求 - 按照文档中的API调用
	req := esapi.SearchRequest{
		Index: []string{"clubs"},
		Body:  strings.NewReader(searchQuery),
	}

	// 执行搜索
	res, err := req.Do(context.Background(), esClient)
	if err != nil {
		return nil, err
	}
	defer res.Body.Close()

	if res.IsError() {
		return nil, fmt.Errorf("搜索失败: %s", res.String())
	}

	// 解析响应
	var r map[string]interface{}
	if err := json.NewDecoder(res.Body).Decode(&r); err != nil {
		return nil, err
	}

	// 提取结果
	var clubs []Club
	hits := r["hits"].(map[string]interface{})["hits"].([]interface{})
	for _, hit := range hits {
		source := hit.(map[string]interface{})["_source"]
		data, _ := json.Marshal(source)

		var club Club
		if err := json.Unmarshal(data, &club); err == nil {
			clubs = append(clubs, club)
		}
	}

	return clubs, nil
}
