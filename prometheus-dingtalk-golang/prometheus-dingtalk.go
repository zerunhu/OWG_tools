package main

import (
	"bytes"
	"context"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"net/url"
	"strings"
	"text/template"
	"time"

	"github.com/Unknwon/goconfig"
	"github.com/gin-gonic/gin"
)

func ListSplitStatus(alerts []interface{}) map[string][]interface{} {
	var firing []interface{}
	var resolved []interface{}
	for _, alert := range alerts {
		if alert.(map[string]interface{})["status"] == "firing" {
			firing = append(firing, alert)
		} else {
			resolved = append(resolved, alert)
		}
	}
	SplitStatus := make(map[string][]interface{})
	SplitStatus["firing"] = firing
	SplitStatus["resolved"] = resolved
	return SplitStatus
	//return firing, resolved
	//golang template package requires functions to return just 1 argument, here is a related fragment (https://golang.org/src/text/template/funcs.go):
	//So, if you want 2 results, you probably need to create your own type and then return it
}

func getConfValue(file string, key string) string {
	cfg, err := goconfig.LoadConfigFile(file)
	if err != nil {
		log.Printf("goconfig.LoadConfigFile err: %v", err)
	}
	value, err := cfg.GetValue("default", key)
	if err != nil {
		log.Printf("cfg.GetValue err: %v", err)
	}
	return value
}

func templateParseFile(json map[string]interface{}) string {
	funcMap := template.FuncMap{"ListSplitStatus": ListSplitStatus}
	//t := template.Must(template.New("letter").Funcs(funcMap).Parse(letter))
	templatePath := getConfValue("conf/conf.ini", "template")
	t, err := template.New("template.tpl").Funcs(funcMap).ParseFiles(templatePath)
	if err != nil {
		log.Printf("template.New err: %v", err)
	}
	buf := bytes.NewBufferString("")
	err = t.Execute(buf, json)
	if err != nil {
		log.Printf("template.Execute err: %v", err)
	}
	return buf.String()
}

func generate_url() string {
	secret := getConfValue("conf/conf.ini", "secret")
	timestamp := time.Now().UnixNano() / 1e6
	sign := fmt.Sprintf("%d\n%s", timestamp, secret)
	h := hmac.New(sha256.New, []byte(secret))
	h.Write([]byte(sign))
	sign_dec := base64.StdEncoding.EncodeToString(h.Sum(nil))
	value := url.Values{}
	value.Set("timestamp", fmt.Sprintf("%d", timestamp))
	value.Set("sign", sign_dec)
	url := getConfValue("conf/conf.ini", "url")
	uri := url + "&" + value.Encode()
	return uri
}

func post_request(text string) {
	apiUrl := generate_url()
	content := `
		{"msgtype": "markdown",
		"markdown": {
						"title": "prometheus",
						"text": "` + text + `"
		}
		}
	`
	request, err := http.NewRequest("POST", apiUrl, strings.NewReader(content))
	if err != nil {
		log.Printf("http.NewRequest err: %v", err)
	}
	request.Header.Set("Content-Type", "application/json;charset=UTF-8")
	client := http.Client{}
	resp, err := client.Do(request.WithContext(context.TODO()))
	if err != nil {
		log.Printf("client.Do err: %v", err)
	}
	respBytes, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		log.Printf("ioutil.ReadAll err: %v", err)
	}
	log.Printf("dingtalk return data: %v", string(respBytes))
}

func main() {
	log.Printf("Welcome to use prometheus-dingtalk, access the interface url: 127.0.0.1:8060/sendDingtalk, use the configuration file .conf/conf.ini, if you have any questions, please visit the address: https://github.com/huzerun0306/OWG_tools")
	gin.SetMode(gin.ReleaseMode)
	router := gin.Default()

	router.POST("/sendDingtalk", func(c *gin.Context) {
		//获取post提交得数据并且格式化json类型为map[string]interface{}
		json := make(map[string]interface{})
		err := c.BindJSON(&json)
		if err != nil {
			log.Printf("c.BindJSON err: %v", err)
		}
		//把获取得json数据经过templateFile得模板转换为具体的可以发送给钉钉的json格式
		text := templateParseFile(json)
		//发送钉钉请求
		post_request(text)
		//response
		c.JSON(200, gin.H{
			"status": "ok",
		})
	})
	router.Run(":8060")
}
