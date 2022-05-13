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
      tweetView: "{{ tweetView }}",
      targetView: "{{ targetView }}",
      maxTweets: {{ maxTweets }},
      tweets: [],
      loading: false,
      baseUrl: "{{ base_url }}/airtable/{{ config_id }}",
      email: "",
      optIn: false
    }
  },
  computed: {
    url(){
      return `${this.baseUrl}/json?targetView=${this.targetView}&tweetView=${this.tweetView}&tweets=${this.maxTweets}`
    }
  },
  methods: {
    getTweets() {
      httpGetAsync(this.url, function(res){
        tweets = JSON.parse(res)['tweets'];
        tweetGenerator.tweets = tweets;
      })
    },
    tweetClicked(tweet){
      httpGetAsync(`${this.baseUrl}/tweeted?email_address=${encodeURIComponent(this.email)}&opt_in=${encodeURIComponent(this.optIn)}&target=${encodeURIComponent(tweet.target.name)}&tweet=${encodeURIComponent(tweet.tweet)}`, function(res){
        console.log(res)
        return;
      })
    }
  }
}).mount('#tweet-generator')
