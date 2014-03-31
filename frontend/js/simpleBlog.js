
var simpleBlogDirective = angular.module('SimpleBlog.directive', []);

var simpleBlogFilter = angular.module('SimpleBlog.filter', []);
simpleBlogFilter.filter('escape', function() {
    return window.encodeURIComponent;
});

var simpleBlogService = angular.module('SimpleBlog.service', [], function($provide) {
    $provide.factory('msgBus', ['$rootScope', function($rootScope) {
        var msgBus = {};
        msgBus.emitMsg = function(msg) {
            $rootScope.$emit(msg);
        };
        msgBus.onMsg = function(msg, scope, func) {
            var unbind = $rootScope.$on(msg, func);
            scope.$on('$destroy', unbind);
        };
        return msgBus;
    }]);
});

var simpleBlog = angular.module('SimpleBlog', ['ngCookies', 'SimpleBlog.service', 'SimpleBlog.directive', 'SimpleBlog.filter'])

simpleBlog.run(['$rootScope', '$location', '$http', function ($rootScope, $location, $http) {
    var pageData = angular.element(document.querySelector('#pageData')).html();
    var blogSetting = angular.element(document.querySelector('#blogSetting')).html();
    $rootScope.pageData = angular.fromJson(pageData);
    $rootScope.blogSetting = angular.fromJson(blogSetting);
    if ($rootScope.pageData.type == "post") {
        $rootScope.pageData.content = angular.element(document.querySelector('#postMd')).html().trim();
    }
    if (window.location.pathname.split('/').length == 3) {
        $rootScope.path = "../";
    } else {
        $rootScope.path = "";
    }
    $rootScope.secureChannel = $location.protocol() == $rootScope.blogSetting.protocol &&
                               $rootScope.blogSetting.domain == $location.host();
    $rootScope.sameDomain = $rootScope.blogSetting.domain == $location.host();

}]);

simpleBlog.controller('blogBodyCrl', ['$scope', '$log', '$http', '$location', '$cookies', 'msgBus', function($scope, $log, $http, $location, $cookies, msgBus) {
        $scope.showModel = false;
        $scope.auth = $cookies.login ? true : false;
        $scope.login = function() {
            if ($scope.secureChannel) {
                $scope.showModel = true;
            }
        };
        $scope.logout = function() {
            $http({
                method: 'GET',
                url: $scope.path + 'logout'
            }).success(function(data, status, headers, config) {
                $scope.showModel = false;
                $scope.auth = false;
            });
        };
        $scope.cancelModal = function() {
            $scope.showModel = false;
        };
        $scope.signin = function() {
            if ($scope.secureChannel) {
                $http({
                    method: 'POST',
                    data: angular.toJson({
                        'username': this.username,
                        'password': this.password
                    }),
                    url: $scope.blogSetting.protocol + '://' + $scope.blogSetting.domain + '/login'
                }).success(function(data, status, headers, config) {
                    $scope.showModel = false;
                    if (status == 200) {
                        var ret = angular.fromJson(data);
                        if(ret.error == 0) {
                            $scope.auth = true;
                        }
                    }
                }).error(function(data, status, headers, config) {
                    $scope.showModel = false;
                });
            }
        };
        $scope.leaveSearchBox = function() {
            msgBus.emitMsg('leaveSearchBox');
        }
    }])
    .controller('searchCrl', ['$scope', '$log', '$http', 'msgBus', function($scope, $log, $http, msgBus) {
        $scope.searchResults = [];
        $scope.showDropdown = false;
        $scope.showIcon = true;
        $scope.leaveSearchBox = function() {
            $scope.showIcon = true;
        };
        $scope.clickSearchIcon = function() {
            $scope.showIcon = false;
            $http({
                method: 'GET',
                url: $scope.path + 'search'
            }).success(function(data, status, headers, config) {
                if (status == 200) {
                    var ret = angular.fromJson(data);
                    if(ret.error == 0) {
                        $scope.searchResults = ret.keyList;
                        $scope.showDropdown = $scope.searchResults.length > 0;
                    }
                }
            });
        };
        $scope.textChange = function() {
            $http({
                method: 'GET',
                url: $scope.path  + 'search?filter=' + this.searchText
            }).success(function(data, status, headers, config) {
                if (status == 200) {
                    var ret = angular.fromJson(data);
                    if(ret.error == 0) {
                        $scope.searchResults = ret.keyList;
                        $scope.showDropdown = $scope.searchResults.length > 0;
                    }
                }
            });

        };

        msgBus.onMsg('leaveSearchBox', $scope, $scope.leaveSearchBox);
    }])
    .controller('navCrl', ['$scope', '$log', function($scope, $log) {
        $scope.navSetting = [
            { name: 'Home', href: $scope.path + 'home.html', selected: $scope.pageData.type == 'post' && $scope.pageData.latest ? 'nav-selected' : '' },
            { name: 'About', href: $scope.path + 'about.html', selected: $scope.pageData.type == 'about' ? 'nav-selected' : '' },
            { name: 'Archive', href: $scope.path + 'archive.html', selected: $scope.pageData.type == 'archive' ? 'nav-selected' : '' },
            { name: 'New', href: $scope.path + 'edit.html', selected: $scope.pageData.type == 'edit' ? 'nav-selected' : '' }
        ];
    }])
    .controller('editPostCrl', ['$scope', '$log', '$element', '$timeout', '$http', '$window', function($scope, $log, $element, $timeout, $http, $window) {
        if($scope.pageData.type == 'edit') {
            $scope.editContent = angular.fromJson($scope.pageData).content;
            $scope.editPostId = angular.fromJson($scope.pageData).postId;
            $scope.textareaHeight = null;
            $timeout(function(){
                // maybe there is a better way
                var newHeight = angular.element(document.querySelector('.edit-post-box'))[0].scrollHeight;
                if(newHeight && ! $scope.textareaHeight) {
                    $scope.textareaHeight = { height: newHeight + 'px' };
                }
            }, 200);
            $scope.textChange = function() {
                var newHeight = angular.element(document.querySelector('.edit-post-box'))[0].scrollHeight;
                if ({ height: newHeight + 'px' } != $scope.textareaHeight) {
                    $scope.textareaHeight = { height: newHeight + 'px' };
                }
            };
            $scope.savePost = function() {
                $http({
                    method: 'POST',
                    data: angular.toJson({
                        'postId': $scope.editPostId,
                        'postContent': this.editContent
                    }),
                    url: $scope.path + '/post'
                }).success(function(data, status, headers, config) {
                    if (status == 200) {
                        ret = angular.fromJson(data);
                        if(ret.error == 0) {
                            $window.location.replace($scope.path + 'post/' + $scope.editPostId + '.html');
                        } else if (ret.error == 4) {
                            alert("Title, Date, Category, Tags are MUST fields; Status MUST be either private or public!");
                        } else{
                            alert('Save post error!');
                        }
                    } else {
                        alert('Save post error!');
                    }
                }).error(function(data, status, headers, config) {
                    alert('Save post error!');
                });
            };
        }
    }])
    .controller('archiveCrl', ['$scope', '$log', '$element', function($scope, $log, $element) {
        if($scope.pageData.type == 'archive') {
            $scope.totalArchives = $scope.pageData.archives;
            $scope.setDisableStatus = function () {
                if($scope.pagingStart <= 0) {
                    $scope.disablePrevious = true;
                } else {
                    $scope.disablePrevious = false;
                }
                if($scope.pagingEnd >= $scope.totalArchives.length) {
                    $scope.disableNext = true;
                } else {
                    $scope.disableNext = false;
                }
            };
            $scope.resetPaging = function() {
                $scope.pagingStart = 0;
                $scope.paingStep = 6;
                $scope.pagination = 6;
                $scope.pagingEnd = Math.min($scope.pagination, $scope.totalArchives.length);
                $scope.archives = $scope.totalArchives.slice($scope.pagingStart, $scope.pagingEnd);
                $scope.setDisableStatus();
            };
            $scope.ClickPrevious = function() {
                if($scope.disablePrevious) {
                    return;
                }
                $scope.pagingStart -= $scope.paingStep;
                $scope.pagingStart = Math.max(0, $scope.pagingStart);
                $scope.pagingEnd = $scope.pagingStart + $scope.paingStep;
                $scope.pagingEnd = Math.min($scope.pagingEnd, $scope.totalArchives.length);
                if($scope.pagingEnd >= $scope.pagingStart) {
                    $scope.archives = $scope.totalArchives.slice($scope.pagingStart, $scope.pagingEnd);
                } else {
                    $scope.resetPaging();
                }
                $scope.setDisableStatus()
            };
            $scope.ClickNext = function() {
                if($scope.disableNext) {
                    return;
                }
                $scope.pagingStart += $scope.paingStep;
                $scope.pagingEnd += $scope.paingStep;
                $scope.pagingEnd = Math.min($scope.pagingEnd, $scope.totalArchives.length);
                if($scope.pagingEnd >= $scope.pagingStart) {
                    $scope.archives = $scope.totalArchives.slice($scope.pagingStart, $scope.pagingEnd);
                } else {
                    $scope.resetPaging();
                }
                $scope.setDisableStatus();
            };
            $scope.resetPaging();
        }
    }])
    .controller('postCrl', ['$scope', '$sce', '$log', '$element', '$http', function($scope, $sce, $log, $element, $http) {
        if($scope.pageData.type == 'post') {
            if (!$scope.pageData.postId) {
                $scope.showPost = false;
                $scope.showReply = false;
            } else {
                $scope.post = {};
                $scope.showPost = true;
                $scope.showPencil = $scope.pageData.status != 'public';
                $scope.post.htmlBody = $sce.trustAsHtml(markdown.toHTML($scope.pageData.content, "Maruku"));
                $scope.post.title = $scope.pageData.postTitle;
                $scope.post.postDate = $scope.pageData.postDate;
                $scope.editURI = $scope.path + 'edit.html?postId=' + $scope.pageData.postId;
                $scope.commentsNum = $scope.pageData.commentsCount;
                $scope.visitCount = $scope.pageData.visitCount;
                $scope.showReply = false;
                if ($scope.sameDomain) {
                    $http({
                        method: 'PUT',
                        data: angular.toJson({postId: $scope.pageData.postId}),
                        url: $scope.path + 'visit'
                    }).success(function(data, status, headers, config) {
                        if (status == 200) {
                            var ret = angular.fromJson(data);
                            if(ret.error == 0 && ret.result) {
                                $scope.post.visitCount = ret.result.count
                            }
                        }
                    });
                    $http({
                        method: 'GET',
                        url: $scope.path + 'comment?postId=' + $scope.pageData.postId
                    }).success(function(data, status, headers, config) {
                        if (status == 200) {
                            var ret = angular.fromJson(data);
                            if(ret.error == 0 && ret.result && ret.result.comments) {
                                $scope.comments = ret.result.comments;
                            }
                        }
                    });
                }
                $scope.crtReplyView = function () {
                    if(! $scope.showReply && $scope.sameDomain) {
                        $scope.showReply = true;
                    } else {
                        $scope.showReply = false;
                    }
                };
                $scope.postComments = function () {
                    // TODO
                };
                $scope.replyUser = function () {
                    // TODO
                };
            }
        }
    }])
    .controller('aboutCrl', ['$scope', '$log', '$sce', '$element', function($scope, $log, $sce, $element) {
        if($scope.pageData.type == 'about') {
            $scope.about = $sce.trustAsHtml(markdown.toHTML($scope.pageData.content, "Maruku"));
        }
    }])
;
