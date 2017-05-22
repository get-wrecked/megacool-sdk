#import <Foundation/Foundation.h>
#import "Tune.h"
#import "UnityAppController.h"
#import <Megacool/Megacool.h>

@interface MergedUnityAppController : UnityAppController

@end

@implementation MergedUnityAppController : UnityAppController

- (void)application:(UIApplication *)application
    handleEventsForBackgroundURLSession:(NSString *)identifier
    completionHandler:(void (^)())completionHandler {

    [[Megacool sharedMegacool]
        handleEventsForBackgroundURLSession:identifier
                          completionHandler:completionHandler];
}


- (BOOL)application:(UIApplication *)application
    continueUserActivity:(NSUserActivity *)userActivity
    restorationHandler:(void (^)(NSArray *))restorationHandler {

    if ([[Megacool sharedMegacool] continueUserActivity:userActivity]) {
        return YES;
    }

    return [Tune handleContinueUserActivity:userActivity
                        restorationHandler:restorationHandler];

}

- (BOOL) application:(UIApplication *)application
             openURL:(nonnull NSURL *)url
   sourceApplication:(nullable NSString *)sourceApplication
          annotation:(nonnull id)annotation {

    [[Megacool sharedMegacool] openURL:url sourceApplication:sourceApplication];

    [Tune handleOpenURL:url sourceApplication:sourceApplication];
    
    return [super application:application
                      openURL:url
            sourceApplication:sourceApplication
                   annotation:annotation];
}

- (BOOL)application:(UIApplication *)app
   openURL:(NSURL *)url
   options:(NSDictionary<UIApplicationOpenURLOptionsKey,id> *)options {

    [[Megacool sharedMegacool] openURL:url options:options];

    [Tune handleOpenURL:url options:options];

    return [super application:app
                      openURL:url
                      options:options];
}

@end

IMPL_APP_CONTROLLER_SUBCLASS(MergedUnityAppController)
