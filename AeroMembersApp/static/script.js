var app = angular.module('myApp', ['ngSanitize','ngCookies']);

app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

app.controller('forumCtrl', ['$scope', '$http', '$sce', '$cookies', '$document', function($scope, $http, $sce, $cookies, $document) {

    $scope.replyForms = {}
    $scope.replies = {}
    var init = function() {
    }

    $scope.upvote = function(postId){
        $http({
            url: window.location.origin+"/upvotepost/",
            method: 'POST',
            data: {'postId':postId}
        }).then(function success(){
            var score = parseInt($document[0].getElementById("postScore_"+postId.toString()).textContent)
            score += 1
            $document[0].getElementById("postScore_"+postId).textContent = score.toString()
            $document[0].getElementById("postScore_"+postId).classList.add("upvoted")
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