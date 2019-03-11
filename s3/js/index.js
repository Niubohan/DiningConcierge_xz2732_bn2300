/// <reference types="aws-sdk" />

AWS.config.region = 'us-east-1';
var cognitoidentity = new AWS.CognitoIdentity();

function getSearchString(key, Url) {
    var str = Url;
    str = str.split("#")[1];;
    var arr = str.split("&");
    var obj = new Object();

    for (var i = 0; i < arr.length; i++) {
        var tmp_arr = arr[i].split("=");
        obj[decodeURIComponent(tmp_arr[0])] = decodeURIComponent(tmp_arr[1]);
    }
    return obj[key];
}

var url = window.location.href;
var token = getSearchString('id_token', url); 

console.log(token);

AWS.config.credentials = new AWS.CognitoIdentityCredentials({
    IdentityPoolId: 'us-east-1:eb59d899-e058-4e1e-b992-4166b4ea5b9d',
    Logins: {
      'cognito-idp.us-east-1.amazonaws.com/us-east-1_lWfflG9J3' : token
    }
});

var credentialsforid = {
    IdentityPoolId: 'us-east-1:eb59d899-e058-4e1e-b992-4166b4ea5b9d',
    Logins: {
      'cognito-idp.us-east-1.amazonaws.com/us-east-1_lWfflG9J3' : token
    }
}

var IdentityId = '';
var apigClient;


cognitoidentity.getId(credentialsforid, function(err, data) {
  if (err) console.log(err, err.stack); // an error occurred
  else {
    console.log(data);
    IdentityId = data.IdentityId;          // successful response
    console.log(IdentityId);
  }

  // test
  var credential = {
    IdentityId: IdentityId,
    Logins: {
      'cognito-idp.us-east-1.amazonaws.com/us-east-1_lWfflG9J3' : token
    }
  }
  
  cognitoidentity.getCredentialsForIdentity(credential, function(err, data) {
    if (err) console.log(err, err.stack); // an error occurred
    else     console.log(data.Credentials);           // successful response

    var AccessKeyId = data.Credentials.AccessKeyId;
    var SecretKey = data.Credentials.SecretKey;
    var SessionToken = data.Credentials.SessionToken;

    console.log(AccessKeyId);

    var newClientCredentials = {
      accessKey: AccessKeyId,
      secretKey: SecretKey,
      sessionToken: SessionToken,
      region: 'us-east-1'
    };
    apigClient = apigClientFactory.newClient(newClientCredentials);
  });
});

$(window).load(function() {
  $message.mCustomScrollbar();
  setTimeout(function() {fakeMessage("Hello!");}, 100);
});

$('.message-submit').click(function() {insertMessage();});

$(window).on('keydown', function(e) {
  if (e.which == 13) {
    insertMessage();
    return false;
  }
})

var $message = $('.messages-content'), d, h, m, i = 0;

function updateScrollbar() {
  $message.mCustomScrollbar("update").mCustomScrollbar('scrollTo', 'bottom', {
    scrollInertia: 10,
    timeout: 0
  });
}

function setDate(){
  d = new Date()
  if (m != d.getMinutes()) {
    m = d.getMinutes();
    $('<div class="timestamp">' + d.getHours() + ':' + m + '</div>').appendTo($('.message:last'));
  }
}

function insertMessage() {
  msg = $('.message-input').val();
  if ($.trim(msg) == '') {
    return false;
  }
  $('<div class="message message-personal">' + msg + '</div>').appendTo($('.mCSB_container')).addClass('new');
  setDate();
  $('.message-input').val(null);
  updateScrollbar();
  var params = {
    // This is where any modeled request parameters should be added.
    // The key is the parameter name, as it is defined in the API in API Gateway.
    param0: 'Accept:application/json',
    "Access-Control-Allow-Headers" : "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
    "Access-Control-Allow-Origin" : '*',
    "Access-Control-Allow-Methods" : "POST"
  };
  var additionalParams = {
    // If there are any unmodeled query parameters or headers that must be
    //   sent with the request, add them here.
    headers: {}
  };
  var unstructured = {
    id : i,
    text : msg,
    timestamp : Date.parse(new Date())
  };
  var messages = [{
    type : "string",
    unstructured : unstructured
  }];
  var body = {
    messages : messages
  };
  i++;
  //setTimeout(function() {
  //  fakeMessage();
  //}, 1000 + (Math.random() * 20) * 100);
  console.log(i);
  apigClient.chatbotPost(params, body, additionalParams)
    .then(function(result){
      console.log(result);
      var mes = result.data.messages[0].unstructured.text;
      console.log(mes);
      fakeMessage(mes);
    }).catch( function(result){
      // Add error callback code here.
      fakeMessage("Sorry, please try again");
    });
}

function fakeMessage(message) {
  if ($('.message-input').val() != '') {
    return false;
  }
  $('<div class="message loading new"><figure class="avatar"><img src="https://s3.amazonaws.com/6998-hw1-xz-bn/fakeavatar.jpg" /></figure><span></span></div>').appendTo($('.mCSB_container'));
  updateScrollbar();

  setTimeout(function() {
    $('.message.loading').remove();
    $('<div class="message new"><figure class="avatar"><img src="https://s3.amazonaws.com/6998-hw1-xz-bn/fakeavatar.jpg" /></figure>' + message + '</div>').appendTo($('.mCSB_container')).addClass('new');
    setDate();
    updateScrollbar();
    i++;
  }, 1000 + (Math.random() * 20) * 100);

}