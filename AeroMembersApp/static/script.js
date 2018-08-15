var app = angular.module('myApp', ['ngSanitize','ngCookies','ui.bootstrap']);

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

app.controller('companyCtrl', ['$scope', '$http', '$sce', '$cookies', '$document', '$window', function($scope, $http, $sce, $cookies, $document, $window) {
    init = function(){
        $scope.newCompany = false;
        $scope.showStart = true;
        $http.get('/getcompanies').then(function success(response){
            $scope.companies = response.data
        })
    }

    $scope.showAddForm = function(){
        return $scope.newCompany && !$scope.showStart
    }

    $scope.showJoinForm = function(){
        return !$scope.newCompany && !$scope.showStart
    }

    init()
}]);

app.controller('subscriptionCtrl', ['$scope','$http','$window',function($scope,$http,$window){

    $scope.selectPlan = function(plan){
        $http({
            url: "/createsubscription/",
            method: 'POST',
            data: {'plan':plan}
        }).then(function success(response){
            $window.location.href = '/subscriptioncheckout/'
        },function error(){
            console.log("Error processing subscription request.")
        })
    }

    $scope.orderAndCheckout = function(item){
        $http({
            url: "/addorderline/",
            method: 'POST',
            data: {'item':item}
        }).then(function success(response){
            $window.location.href = '/checkout/'
        },function error(){
            console.log("Error adding order line.")
        })
    };
}]);

app.controller('subscriptionCheckoutCtrl', ['$scope','$http','$window',function($scope,$http,$window){
    init = function(){
        //load selected plan
        // $http({
        //     url: "/getinactivesubscription/",
        //     method: 'GET',
        // }).then(function success(response){
        //     $scope.subscription = response.data[0]
        //     if ($scope.subscription['discount__rate'] != undefined){
        //         $scope.totalPrice = $scope.subscription['plan__monthlyRate']*$scope.subscription['discount__rate']                
        //     }
        //     else{
        //         $scope.totalPrice = $scope.subscription['plan__monthlyRate']
        //     }
        // },function error(){
        //     console.log("No order found sorry")
        // })




        $http({
            url: "/clienttoken/",
            method: 'GET'
        }).then(function success(response){
            $scope.showAddPaymentMethod = true
            braintree.dropin.create({
                  authorization: response.data,
                  container: '#braintree-dropin'
                }, function (createErr, instance) {
                    $scope.braintreeDropin = instance
                });
        },function error(){
            console.log("Client token not received.")
        })
    }

    $scope.selectPlan = function(plan){
        $http.get('/getplan/'+plan).then(function success(response){
            $scope.selectedPlan = response.data
            $scope.selected = true
            $scope.discount = 0
        },function error(response){
            console.log("Error retrieving plan details")
        })
    }

    $scope.addPaymentMethod = function(){
        $scope.braintreeDropin.requestPaymentMethod(function (err, payload) {
              $http({
                url: "/addpaymentmethod/",
                method: 'POST',
                data: {'paymentNonce':payload.nonce}
              }).then(function success(response){
                $scope.paymentMethods['creditCard'].push(response.data['creditCard'])
                $scope.paymentMethods.paypal.push(response.data.paypal)
              },function error(){
                console.log("Error processing adding payment method")
              })
            });
    };

    $scope.pay = function () {
        $scope.braintreeDropin.requestPaymentMethod(function (err, payload) {
            $http({
                url: "/subscriptioncheckout/",
                method: 'POST',
                data: {'paymentNonce':payload.nonce,
                        'planId':$scope.selectedPlan.id,
                        'discountCode':$scope.discountCode}
            }).then(function success(response){
                console.log("Payment was successful")
                $window.location.href = '/'
            },function error(err){
                console.log("Error processing your payment")
            })
        })
    };

    $scope.applyDiscount= function(code){
        $http({
                url: "/applydiscount/",
                method: 'POST',
                data: {'discountCode':code}
              }).then(function success(response){
                $scope.discount = response.data
                //loadOrder(response.data)
              },function error(){
                console.log("Error processing discount")
              })
    }

    // $scope.cancelSubscription=function(braintreeID){
    //     $http.get("/cancelSubscription/"+braintreeID.toString()).then(function success(response){
            
    //     }, function error(){
    //         console.log("Error canceling your subscription")
    //     })
    // }

    init();
    
}]);


app.controller('checkoutCtrl', ['$scope','$http',function($scope,$http){
    var button = document.querySelector('#submit');
    /*$http({
            url: "/clienttoken/",
            method: 'GET'
        }).then(function success(response){
            braintree.dropin.create({
                  authorization: response.data,
                  container: '#dropin-container'
                }, function (createErr, instance) {
                  button.addEventListener('click', function () {
                    instance.requestPaymentMethod(function (err, payload) {
                      $http({
                        url: "/paymentnonce/",
                        method: 'POST',
                        data: {'paymentNonce':payload}
                      })
                    });
                  });
                });
        },function error(){
            console.log("Client token not received.")
        })

    $scope.purchaseSubscription = function(membershipType){
        $http({
            url: "/clienttoken/",
            method: 'GET'
        }).then(function success(response){
            braintree.dropin.create({
                  authorization: response.data,
                  container: '#subscribe-payment-container'
                }, function (createErr, instance) {
                  button.addEventListener('click', function () {
                    instance.requestPaymentMethod(function (err, payload) {
                      $http({
                        url: "/subscribeuser/",
                        method: 'POST',
                        data: {'paymentNonce':payload.nonce,
                                'membership':$scope.membershipSelected}
                      }).then(function success(response){
                        console.log("Payment was successful")
                      },function error(){
                        console.log("Error processing your payment")
                      })
                    });

                  });
                });
        },function error(){
            console.log("Client token not received.")
        })
    }
    */

    init = function(){
        //load active order
        $http({
            url: "/getorder/",
            method: 'GET',
        }).then(function success(response){
            loadOrder(response.data)
        },function error(){
            console.log("No order found sorry")
        })

        $http({
            url: "/clienttoken/",
            method: 'GET'
        }).then(function success(response){
            $scope.showAddPaymentMethod = true
            braintree.dropin.create({
                  authorization: response.data,
                  container: '#braintree-dropin'
                }, function (createErr, instance) {
                    $scope.braintreeDropin = instance
                });
        },function error(){
            console.log("Client token not received.")
        })
    }

    loadOrder = function(orderLines){
        if(orderLines.length == 0){
            $scope.emptyCart = true
        }
        else{
            $scope.emptyCart = false
            $scope.order = orderLines
            prices = orderLines.map(o => o.price)
            $scope.totalPrice = prices.reduce((t,o) => t+o)            
        }
    }

    $scope.addPaymentMethod = function(){
        $scope.braintreeDropin.requestPaymentMethod(function (err, payload) {
              $http({
                url: "/addpaymentmethod/",
                method: 'POST',
                data: {'paymentNonce':payload.nonce}
              }).then(function success(response){
                $scope.paymentMethods['creditCard'].push(response.data['creditCard'])
                $scope.paymentMethods.paypal.push(response.data.paypal)
              },function error(){
                console.log("Error processing adding payment method")
              })
            });
    };

    $scope.pay = function () {
        $scope.braintreeDropin.requestPaymentMethod(function (err, payload) {
            $http({
                url: "/payment/",
                method: 'POST',
                data: {'paymentNonce':payload.nonce}
            }).then(function success(response){
                console.log("Payment was successful")
                $window.location.href = '/'
            },function error(err){
                console.log("Error processing your payment")
            })
        })
    };

    $scope.applyDiscount= function(code,orderLine){
        $http({
                url: "/applydiscount/",
                method: 'POST',
                data: {'discountCode':code}
              }).then(function success(response){
                loadOrder(response.data)
              },function error(){
                console.log("Error processing discount")
              })
    }

    $scope.cancelLine = function(orderLine){
        $http({
                url: "/cancelorderline/",
                method: 'POST',
                data: {'orderLine':orderLine}
              }).then(function success(response){
                loadOrder(response.data)
              },function error(){
                console.log("Error canceling discount")
              })
    }

    init()
    
}]);

app.controller('dynamicGridCtrl', ['$scope', '$http', '$sce', '$cookies', '$document', '$window', function($scope, $http, $sce, $cookies, $document, $window) {
    function init(){
        $http.get('members/').then(function success(response){
            $scope.members = response.data
        })
    }
    $scope.invitees = [{}]
    $scope.companyMembers = []
    var changes = []

    $scope.addInput = function(){
        $scope.invitees.push({})
    }
    $scope.submit = function(url){
        $scope.invitees = $scope.invitees.filter(invitee => Object.keys(invitee).length > 1)
        $http.post(url,{'invitees':$scope.invitees}).then(function success(){
            alert("Invites successfully sent to "+$scope.invitees.map(invitee => invitee.email).join(', '))
        }), function error(response){
            alert(response.data)
        }
    }

    $scope.addRow = function(entry){
        newRow = {'email':entry.email,'isAdmin':entry.isAdmin,'action':'ADD'}
        $scope.members.push(newRow)
        changes.push(newRow)
    }

    $scope.removeRow = function(i){
        if($scope.members[i].action == undefined){
            changes.push({'email':$scope.members[i].email, 'action':'REMOVE'})
        }
        $scope.members.splice(i,1)
    }    

    $scope.editRow = function(email,isAdmin){
        found = false
        changes.forEach(function(change){
            if (change.email == email){
                change.isAdmin = isAdmin
                found = true
                break
            }
        })
        if(!found){
            changes.push({'email':email, 'isAdmin':isAdmin, 'action':'EDIT'})
        }
    }

    $scope.save = function(){
        $http.post('',changes).then(function success(response){
            alert('Changes have been saved')
        }, function error(response){
            alert(response.data)
        })
    }

    init()
}]);