package http

import "github.com/gin-gonic/gin"

func NotFoundResponse(c *gin.Context, err error) {
	c.IndentedJSON(404, gin.H{
		"status": false,
		"error":  err.Error(),
		"data":   gin.H{},
	})
}

func OKResponse(c *gin.Context, data gin.H) {
	c.IndentedJSON(200, gin.H{
		"status": true,
		"data":   data,
	})
}

func UnauthorizedResponse(c *gin.Context, err error) {
	c.IndentedJSON(403, gin.H{
		"status": false,
		"error":  err.Error(),
		"data":   gin.H{},
	})
}
