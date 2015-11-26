uauth = angular.module('uauth', ['ngCookies']);

uauth.run(["$templateCache", function($templateCache) {
	$templateCache.put("alert.html",
		"<div class='alert alert-{{type}}'>\n" +
		"    <button ng-show='closeable' type='button' class='close' ng-click='close()'>&times;</button>\n" +
		"    <p>{{message}}</p>\n" +
		"</div>\n");
}]);

uauth.config(function($locationProvider,$routeProvider) {
	$locationProvider.html5Mode(true);
});

SignupCtrl = uauth.controller("SignupCtrl", function($scope,$http,$timeout) {
	$scope.userset = false;
	$scope.alerts = [];
	$scope.alertNum = function(etype,emsg){
		for (counter in $scope.alerts) {
			alert = $scope.alerts[counter]
			if (alert.type == etype & alert.msg == emsg){
				return counter
			};

		};
	}
	$scope.timedAlert = function(etype, emsg,time){
		$scope.addAlert(etype,emsg)
		$timeout(function(){
			num = $scope.alertNum(etype,emsg)
			$scope.closeAlert(num)
		}, time)
	};
	$scope.addAlert = function(etype, emsg) {
		$scope.alerts.push({type:etype, msg:emsg});		
	};

	$scope.closeAlert = function(index) {
		$scope.alerts.splice(index, 1);
	};
	

	$scope.check_username = function() {
		
		config = {
			url: '/already/u',
			method: "POST",
			data: $scope.username
		}
		$http(config).success(function(data){
			if(data == "true"){
				$scope.addAlert("error","Username is already registered")
			}
			if(data == "false"){
				num = $scope.alertNum("error","Username is already registered")
				$scope.closeAlert(num)
			}
		}).error(function(){
			console.log("Username check failed," + data)
		});
	};
	$scope.check_email = function() {
		
		config = {
			url: '/already/e',
			method: "POST",
			data: $scope.email
		}
		$http(config).success(function(data){
			if(data == "true"){
				$scope.addAlert("error","Email is already registered")
			}
			if(data == "false"){
				num = $scope.alertNum("error","Email is already registered")
				$scope.closeAlert(num)
			}
		}).error(function(){
			console.log("Email check failed," + data)
		});
	};
	$scope.submit = function(){
		if (!$scope.first || !$scope.last || !$scope.username || !$scope.email || !$scope.password){
			$scope.timedAlert("error","Please fill out all fields before submitting", 2000)
			return 
		}
		info = {
			first: $scope.first,
			last: $scope.last,
			username: $scope.username,
			email: $scope.email,
			password: $scope.password
		}
		config = {
			url: '/signup',
			method: "POST",
			data: JSON.stringify(info),
			headers: {'Content-Type': 'application/json'}
		};

		$http(config).success(function(data){
			if(data == "Failure"){
				$scope.addAlert("error","We had a server problem, sry try again")
			}
			else {
				$scope.userset = true;
				$scope.valink = data;	
				$scope.addAlert("success","Great your all set up, click on the check to verify your account")
			}
		}).error(function(){
			console.log("Sign up Fail")
		});
	};
});
LoginCtrl = uauth.controller("LoginCtrl", function($scope, $http, $window){
	$scope.alertNum = function(etype,emsg){
		for (counter in $scope.alerts) {
			alert = $scope.alerts[counter]
			if (alert.type == etype & alert.msg == emsg){
				return counter
			};

		};
	}
	$scope.timedAlert = function(etype, emsg,time){
		$scope.addAlert(etype,emsg)
		$timeout(function(){
			num = $scope.alertNum(etype,emsg)
			$scope.closeAlert(num)
		}, time)
	};
	$scope.addAlert = function(etype, emsg) {
		$scope.alerts.push({type:etype, msg:emsg});		
	};

	$scope.closeAlert = function(index) {
		$scope.alerts.splice(index, 1);
	};

	$scope.submit = function(){
		if (!$scope.username || !$scope.password){
			$scope.timedAlert("error","Please fill out both fields before submitting", 2000)
			return 
		}	
		info = {
			username: $scope.username,
			password: $scope.password
		}
		config = {
			url: '/login',
			method: "POST",
			data: JSON.stringify(info),
			headers: {'Content-Type': 'application/json'}
		};

		$http(config).success(function(data){
			if(data == "Failure"){
				$scope.addAlert("error","Either your Username or Password is incorect, please try again")
			}
			else {
				$window.location.href = "/authenticated"
			}
		}).error(function(){
			console.log("Log in Fail")
		});
	}	

})
HomeCtrl = uauth.controller('HomeCtrl', function($cookies, $scope, $window, $http){
	config = {
		url: '/user',
		method: "POST",
		data: "User"
	}
	$http(config).success(function(data){
		$scope.user = data
	}).error(function(){
		console.log("Auth Error")
	})
	
})
uauth.directive('alert', function () {
	return {
		restrict:'E',
		templateUrl:'alert.html',
		replace:true,
		scope: {
			message: '=',
			type: '=',
			close: '&'
		},
		link: function(scope, iElement, iAttrs, controller) {
			scope.closeable = "close" in iAttrs;
		}
	};
});