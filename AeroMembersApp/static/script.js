var app = angular.module('myApp', ['ngSanitize','ngCookies']);

app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);


app.controller('forumCtrl', ['$scope', '$http', '$sce', '$cookies', '$document', '$window', function($scope, $http, $sce, $cookies, $document, $window) {
    
    $http({
            url: "comments/",
            method: 'GET',
        }).then(function success(response){
            $scope.comments = response.data.comments
            $scope.threadId = response.data.threadId
            $scope.user = response.data.user
        },function error(){
            console.log("No comments found")
        })

    $scope.upvoteComment = function(comment){
        $http({
            url: "/upvotecomment/",
            method: 'POST',
            data: {'commentId':comment.id}
        }).then(function success(){
            comment.score = (parseInt(comment.score) + 1).toString()
        },function error(){
            console.log("This user has already upvoted")
        })
    }

    $scope.upvoteThread = function(threadId){
        $http({
            url: "/upvotepost/",
            method: 'POST',
            data: {'postId':threadId}
        }).then(function success(){
            var score = parseInt($document[0].getElementById("threadScore").textContent)
            score += 1
            $document[0].getElementById("threadScore").textContent = score.toString()
            $document[0].getElementById("threadScore").classList.add("upvoted")
        },function error(){
            console.log("This user has already upvoted")
        })
    }

    $scope.deleteComment = function(commentId){
        $window.location.href = 'deletepost/'+commentId;
    }


}]);

app.controller('braintreeCtrl', ['$scope','$http',function($scope,$http){
    var button = document.querySelector('#submit-button');
    $http({
            url: "/clienttoken/",
            method: 'GET'
        }).then(function success(){
            braintree.dropin.create({
                  authorization: 'CLIENT_TOKEN_FROM_SERVER',
                  container: '#dropin-container'
                }, function (createErr, instance) {
                  button.addEventListener('click', function () {
                    instance.requestPaymentMethod(function (err, payload) {
                      // Submit payload.nonce to your server
                    });
                  });
                });
        },function error(){
            console.log("Client token not received.")
        })
    
}]);