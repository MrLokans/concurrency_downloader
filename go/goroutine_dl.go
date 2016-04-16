package main

import (
	"fmt"
	"os"
    "io"
	"net/http"
)

func DownloadFileByUrl(url string, filepath string) (err error) {

	// Create the file
	out, err := os.Create(filepath)
	if err != nil {
		return err
	}
	defer out.Close()

	// Get the data
	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	// Writer the body to file
	_, err = io.Copy(out, resp.Body)

	if err != nil {
		return err
	}

	return nil
}

func main() {
	var SAMPLE_DOWNLOAD_FILE string = "http://download.thinkbroadband.com/10MB.zip"

	fmt.Println("Downloading ", SAMPLE_DOWNLOAD_FILE)
    
    DownloadFileByUrl(SAMPLE_DOWNLOAD_FILE, "test.zip")
}
