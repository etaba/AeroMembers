var app = angular.module('myApp', ['ngSanitize','ngCookies']);

app.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);


app.controller('forumCtrl', ['$scope', '$http', '$sce', '$cookies', '$document','$timeout', function($scope, $http, $sce, $cookies, $document, $timeout) {
    
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

app.directive("commentTree", function($compile) {
    return {
        restrict: "E",
        transclude: true,
        scope: {comment: '=',test2: '='},
        templateUrl:"/commenttemplate",
        
        compile: function(tElement, tAttr, transclude) {
            var contents = tElement.contents().remove();
            var compiledContents;
            return function(scope, iElement, iAttr) {
                if(!compiledContents) {
                    compiledContents = $compile(contents, transclude);
                }
                compiledContents(scope, function(clone, scope) {
                         iElement.append(clone); 
                });
            };
        }
    };
});