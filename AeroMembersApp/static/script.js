var app = angular.module('myApp', ['ngSanitize','ngCookies']);

app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);


app.controller('forumCtrl', ['$scope', '$http', '$sce', '$cookies', '$document','$timeout', function($scope, $http, $sce, $cookies, $document, $timeout) {

    $scope.comments = {}

    $http({
            url: "comments/",
            method: 'GET',
        }).then(function success(response){
            $scope.comments = response.data
 
        },function error(){
            console.log("This user has already upvoted")
        })

    $scope.upvote = function(postId){
        $http({
            url: window.location.origin+"/upvotepost/",
            method: 'POST',
            data: {'postId':postId}
        }).then(function success(){
            $scope.comments[postId].score = (parseInt($scope.comments[postId].score) + 1).toString()
        },function error(){
            console.log("This user has already upvoted")
        })
    }

    $scope.upvoteThread = function(threadId){
        $http({
            url: window.location.origin+"/upvotepost/",
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


}]);