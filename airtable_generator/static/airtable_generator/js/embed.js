function httpGetAsync(theUrl, callback) {
  let xmlHttpReq = new XMLHttpRequest();
  xmlHttpReq.onreadystatechange = function () {
    if (xmlHttpReq.readyState == 4 && xmlHttpReq.status == 200)
      callback(xmlHttpReq.responseText);
  }
  xmlHttpReq.open("GET", theUrl, true); // true for asynchronous
  xmlHttpReq.send(null);
}
var tweetGenerator = Vue.createApp({
  data() {
    return {
      tweetView: "",
      targetView: "",
      maxTweets: 4,
      tweets: [],
      loading: false
    }
  },
  computed: {
    url(){
      return `http://localhost:3456/airtable/1/json?targetView=${this.targetView}&tweetView=${this.tweetView}&tweets=${this.maxTweets}`
    }
  },
  methods: {
    getTweets() {
      httpGetAsync(this.url, function(res){
        tweets = JSON.parse(res)['tweets'];
        tweetGenerator.tweets = tweets;
      })
    }
  }
}).mount('#tweet-generator')
console.log(tweetGenerator)
