Changelog
=========

The Megacool SDK adheres to [semantic versioning.](http://semver.org)

2.4.0-rc1 - 2017-05-10
======================

First release that supports Android for Unity! Not entirely at feature parity with iOS yet, we'll
be gradually fixing  the discrepancies in upcoming releases. The following doesn't work on Android
yet:

- No share fallback images
- No last frame overlays
- No cropping
- No custom share buttons
- Recordings have to be stopped before they can be previewed or shared
- The `RECEIVED_SHARE_OPENED` events are never fired
- Not all classes are namespaced yet and might create conflicts
- Previews do not support IncludeLastFrameOverlay
- Some actions are pretty slow (rendering preview, share)

Any and all feedback you have from trying it out is greatly appreciated.


## Fixed
- Android: Referral codes containing `-` or `_` were parsed only partially.


2.3.0 - 2017-04-26
==================

First Android release! Only supports native Android for now, Unity will hopefully come Real Soon
Now(tm). Mostly on feature parity with iOS, except the following:
- Custom share buttons
- Recordings have to be stopped before they can be previewed or shared
- Cropping isn't entirely operational yet

While we hope you don't encounter any stacktraces or crashes that originate from us, if you do
please send them our way, we can only fix what we're aware of.

Head over to https://docs.megacool.co/quickstart/android to get started!

## Removed
- **Unity**: Earlier releases included an unused `Google.*Resolver.dll` files, these have been removed to
  avoid conflict with other projects that actually use them.


2.2.4 - 2017-04-14
==================

## Fixed
- The fix from 2.2.2 to ensure frame width is divisible by 4 didn't catch all cases, this has now
  been fixed.
- Blurry last frame overlay on some devices.


2.2.3 - 2017-03-29
==================

## Fixed
- Fix "duplicate symbol" linker errors that could occur in some configurations.


2.2.2 - 2017-03-27
==================

## Fixed
- iOS native: Visually broken GIF if frame width was not divisible by 4.
- All code is now built for minimum iOS version 7.0. Some code was targeting 9.3, causing warnings
 in XCode but otherwise harmless.


2.2.1 - 2017-03-23
==================

## Fixed
- Bitcode is now embedded in all iOS builds
- **Unity: Default gif size is now the same as on native iOS**, half of screen size but at least 200x200 (was
  fixed at 256px wide).


2.2.0 - 2017-02-24
==================

## Added
- You can now **choose how the GIF color table is computed**. It can either be a fixed set of 256
  colors, or based on the colors in the first frame of the GIF.

## Fixed
- The **last frame overlay in preview** now correctly overlays on the last frame, instead of being
  appended as a separate frame.
- **Unity: Significantly higher capture performance** due to capturing frames directly from
  Metal/OpenGL.
- Unity: Showing previews now offload more work to background threads to avoid blocking the main
  thread on load.


2.1.2 - 2016-12-16
==================

## Added
- A **default last frame overlay** can now be set on the Megacool singleton, in addition to the
  existing method where it's set in the config value to `presentShareWithConfig`.
- **Include last frame overlay in previews** by passing
  `kMCLConfigIncludeLastFrameOverlayKey: [NSNumber numberWithBool:YES]` to
  `renderPreviewWithConfig`. Note that the overlay needs to be set with the newly introduced default
  overlay on the singleton for this to work, not using `kMCLConfigLastFrameOverlayKey` when calling
  `presentShareWithConfig`.

## Fixed
- **Unity: `FallbackImage` and `LastFrameOverlay` paths have been made relative to `StreamingAssets`** to
  make them easier to work with.
- **Unity: Universal link support is now compatible with Unity version 5.5**.


2.1.1 - 2016-11-16
==================

## Fixed
- Regression from 2.0.7 where the GIF previews on Unity didn't scale properly on PLUS devices.


2.1.0 - 2016-11-14
==================

## Changed
- **`appConfig` has a new format**, making old configs invalid. Get your new config strings from
  [the dashboard](https://dashboard.megacool.co/games).
- **The SDK now requires that you link with `libz1.2.5`**, since we now compress some of the data
  we store on disk and send over the network for lower overhead. Instructions for adding linked
  libraries can be found [here](https://docs.megacool.co#1-add-frameworks).

## Added
- **Share directly to Messages, Messenger, Mail and Twitter**. We now expose some new methods on the
  `sharedMegacool` instance that will open a share modal for a given channel directly, instead of
  going via the system share sheet. This enables us to share working GIFs to Twitter and Messenger,
  and streamline sharing to Messages and Mail. Read
  [the docs](https://docs.megacool.co#3-1-share-directly-to-channels) for more.

## Deprecated
- **`openShareModal` has been renamed to `presentShare`**. The old name has been deprecated and will
  be removed in a future release.


2.0.7 - 2016-11-03
==================

## Fixed
- Positioning and scaling of GIF previews on iPhone (Plus) devices has been corrected for Unity
  games.


2.0.6 - 2016-10-10
==================

## Fixed
- A regression from 1.2.x where the locale used for timestamps internally wasn't fixed, causing
  users with custom calendar from being rejected by the API for using an invalid date format.
- `startRecording` could cause unbounded growth of the capture queue if the device couldn`t capture
  fast enough to satisfy the desired frame rate (would typically occur on hi-res devices as the
  iPad).


2.0.5 - 2016-10-07
==================

## Fixed
- Ensure app doesn't crash if view is mutated during a capture
- Cropping is now restricted to the intersection of the crop rectangle and the view, ensuring that
  there are no transparent areas in the resulting gif.
- Cropping from top and left now actually works


2.0.4 - 2016-10-05
==================

## Fixed
- Existing games upgrading from 1.2.x with a zeroed-out IDFA would all be assigned the same
  identity, this has been fixed. Any devices with a zeroed-out identity from this bug will get a
  new identity.


2.0.3 - 2016-10-04
==================

## Fixed
- GIF previews in Unity should now be positioned correctly.


2.0.2 - 2016-09-30
==================

## Fixed
- Gif recording wasn't properly disabled on iOS7 before the device had hit the network,
  potentially causing a crash if the recording finished before getting a network reply.


2.0.1 - 2016-09-29
==================

## Fixed
- Removed all sharing channels that started with "Import to ..." or "Copy to ..." which locked the
 `openShareModal` on subsequent taps.


2.0.0 - 2016-08-31
==================

## Changed
- `captureFrame` is now stateless and does not require a corresponding call to `pauseRecording`
  to be persisted. This also leads to a great performance increase compared to calling
  `pauseRecording` manually all the time.
- Stored recordings are no longer deleted from disk regularly to limit disk usage, this is now all
  or nothing, assuming that an app either allows users to see previous recordings or not. This is
  triggered with the config parameter `keepCompletedRecordings` mentioned above.
- The `startWithAppConfig:andEventHandler` eventHandler in Megacool.h now passes an array of
  MCLEvents instead of dictionaries
- Rename `callBackWithParams` type for `startWithAppConfig:andEventHandler` to
  `MCLEventHandlerCallback`
- `continueUserActivity:` has been made an instance method instead of class method, so your handler
  should be changed from `[Megacool continueUserActivity:userActivity]` to
  `[[Megacool sharedMegacool] continueUserActivity:userActivity]`. If you're using the
  `MEGACOOL_DEFAULT_LINK_HANDLERS` macro this is done automatically.
- `handleDeepLink` has been made an instance method instead of class method, so your
  `application:openURL:options` (iOS 9 and above) and
  `application:openURL:sourceApplication:annotation` (<iOS 9) should be changed from
  `[Megacool handleDeepLink:url]` to `[[Megacool sharedMegacool] handleDeepLink:url]`. This is done
  automatically if you're using the `MEGACOOL_DEFAULT_LINK_HANDLERS` macro.
- To detect re-installs locally and not credit them as a new install we save data to the Keychain
  that will persist across re-installs, thus apps now need to link against the `Security.framework`
  to provide access to the Keychain.
- `getReferralLink` has been renamed to `getUserId` to more accurately reflect what it actually
  does, and now requires a callback function that will receive the user id. This is done since
  the user id is set remotely and needs to be communicated from the backend, and is thus
  unavailableit until communication is established. If we've already received the user id from
  the backend the callback will be called immediately, otherwise it will be called as soon as we've
  received it.
- `debugMode` has been renamed to `debug` and is now a class property, if you used this you should
  change `[Megacool sharedMegacool].debugMode = YES;` to `Megacool.debug = YES`.
- GIF uploads are now done in the background to ensure they complete even if the app is
  closed after a share. For this to work you need to add a delegate method
  ```
  -(void)application:(UIApplication *)application
      handleEventsForBackgroundURLSession:(NSString *)identifier
      completionHandler:(void (^)())completionHandler;
  ```
  on your `AppDelegate` that calls `[Megacool sharedMegacool]
  handleEventsForBackgroundURLSession:identifier:completionHandler:completionHandler]`. This is
  done for you automatically if you're using the `MEGACOOL_DEFAULT_LINK_HANDLERS` macro.

## Removed
- `maxFramesOnDisk` has been removed in favor of the new `keepCompletedRecordings` flag. This was
  exempt from the normal deprecation cycle since we're not aware of anyone using this for anything.
- Since disk persistency of GIFs is now the default operation for all timelapse GIFs it is no
  longer possible to disable this from `disableFeatures` with the `kMCFeatureGifPersistency`
  constant. You can instead set `kMCFeatureGif` to disable GIFs entirely.
- `disableGIF` has finished it's deprecation cycle as started in 1.1 and has been removed.

## Added
- `Megacool.keepCompletedRecordings` has been added as an option, which selects whether completed
  recordings should be kept around or not. If you want to let your users watch or re-share previous
  recordings you should set this to `YES`. Default is `NO`, which means whenever a new recording is
  started, completed recordings are deleted. This makes sure that a completed recording is
  available for share until a new one is started. Paused recordings that are not completed is
  unaffected by this.
- `deleteRecording:(NSString *)recordingId` has been added to allow you to remove all traces of a
  recording from disk, completed or not. Useful if you're keeping completed recordings around but
  want to enable users to remove uninteresting recordings that are just hogging disk space.
- `maxFrames` and `frameRate` can now also be set independently for each recording through the
  `config` dictionary to `captureFrame` and `startRecording` by setting the `kMCConfigMaxFramesKey`
  or `kMCConfigFrameRateKey` keys.
- `MCLShare` holds information about a share, like which state it has (sent, clicked, opened,
  installed), the URL and custom data.
- `MCLEvent` is passed in the callback of `startWithAppConfig:andEventHandler` soon after
  the app opens. It also contains a `MCLShare` object if it was sent as part of the share.
- `openShareModalIn:withConfig` now accepts a `MCLShare` as input where you can customize the
  shared URL and add custom data that will be sent to the receiver. Pass this under the key
  `kMCConfigShareKey`.
- Detecting a referred install can now happen faster since it can be detected locally in some
  cases. Thus when starting your app you should start your normal flow, then if the event
  `MCEventLinkClicked` is emitted a link click was detected locally and you can fetch the URL to
  navigate to from the event's `.data[@"MCEventDataURL"]` property. If this was a referred
  install, the `isFirstSession` attribute on the event **might** be set to YES (most installs
  require checking with the backend whether it was referred or not). After contacting the backend to
  fetch the share data associated with the link click, a `MCEventReceivedShareOpened` event will be
  fired. Inspect the share on the event to fetch the data you passed when initiating the share on
  the other end.
- The static method `[Megacool resetIdentity]` can be used to reset a device, effectively making it
  a new device as far as the SDK is concerned, making it easier to test referral flows on a single
  device. Add the call before `+startWithAppConfig` and terminate the app after sending a share,
  if you now click the share you sent the app will open as if you were on another device.

## Fixed
- `openShareModal` had a race condition that could exclude results from recent calls to
  `captureFrame`/`startRecording`.
- A race condition that could crash the app when sending startup requests to the server was fixed.
- Calling `captureFrame` with `forceAdd=YES` had a race condition that might cause the last frames
  before the call with `forceAdd=YES` to be lost.
- Removed memory leak if creating the GIF failed due to full file system or other IO error
- A full file system could cause a full crash of the app because an error condition was not
  checked, this is now handled gracefully.
- You can now capture from an `UIImageView` without getting a blank gif
- The IDFA is no longer used as the primary device identifier, thus the SDK should now correctly
  handle attribution in Test Flight and when the IDFA has been reset or switched off (as can be
  done in iOS10).
- A race condition that prevented requesting deferred urls on install that occured almost all the
  time on iOS 10 and occasionally on earlier operating system has been fixed.


1.2.5 - 2016-04-22
==================

## Fixed
- A race condition between calling `captureFrame` and `pauseRecording` that might prevent any
  frames from being captured at all was found and fixed.


1.2.4 - 2016-04-20
==================

## Added
- The SDK now reports the sending app's version and build to the API, which
  enables the API to show how statistics changed between versions.
- `openShareModalIn:withConfig` now accepts an `UIImage` `fallbackImage` (also available as
  `kMCConfigFallbackImageKey`) as a in-memory alternative to the `fallbackImageURL` key.

## Changed
- Issues submitted with `debugMode=YES` now also includes log messages printed by the SDK during
  the run.

## Fixed
- Outdated frames on disk are now deleted much more efficiently
- There was a race condition between deleting old frames from disk and writing new ones that could
  cause lost frames. This has been fixed.
- Loading previusly recorded frames from disk was found to be very racy and could cause lots of
  undefined treatment of recorded frames.


1.2.3 - 2016-04-18
==================

## Added
- Debug mode that traces SDK usage and submits debug data to Megacool, to more easily reproduce
  issues.

## Fixed
- Race condition between calling captureFrame and stopRecording has been fixed to ensure no frames
  are dropped in between.


1.2.2 - 2016-03-31
==================

## Fixed
- Two bugs that prevented creating multiple GIFs in a row without capturing any
  extra frames in between has been identified and fixed.
- Recordings would not always be stopped if the persistency had been disabled
  between starting and calling pause, this is now fixed.
- Several race conditions that might have caused lost frames between calls to `captureFrame` and
  `pauseRecording` have been removed.


1.2.1 - 2016-03-29
==================

## Fixed
- Bug where the wrong frames on disk would be deleted on startRecording


1.2.0 - 2016-03-25
==================

## Added
- Recording persistency. You can now start a recording with an ID to retrieve or
  resume it later. Frames are stored on disk with this feature.
- MegacoolConstants.h is added, with all the constants you'll use for configs

## Fixed
- Turned off dSYM debug information
- GIFs are now at least 200x200px to auto play on Facebook

## Deprecated
- renderPreviewOfGifWithFrame:frame has been renamed to
  renderPreviewOfGifWithConfig:config. The old syntax will continue to work until
  next major release.
- disableGIF. Use disableFeatures instead, which enables disabling more than just
  GIFs.


1.1 - 2016-02-18
===============

## Added
- SafariServices.framework (iOS 9 +) is recommended to include. Megacool SDK
  uses the cookies match the player to generatedInstall events.
- captureFrame and startRecording now accepts a parameter "crop" which will
  crop the created gif to the area specified.
- openShareModalIn now accepts a config dictionary.
- You can provide a fallback image to openShareModalIn config if no
  gif is created.
- You can add a custom overlay to the last gif frame in openShareModalIn
  config.
- Capturing by frames now supports a new mode - timelapses. See docs for
  Timelapse for more info.


## Fixed
- Gif wasn't created if only one frame was captured

## Deprecated
- openShareModalIn:view fromSourceView:sourceView has been renamed to
  openShareModalIn:view withConfig:@{@"fromSourceView": sourceView}. The old
  syntax will continue to work until next minor release.


1.0.5 - 2016-01-13
==================

## Fixed
- Less disk IO in a several common circumstances
- A bug caused events to be submitted several times, now there's less
  network IO since each event is sent only once
- Share events are now directly associated with a gif if present,
  increasing the precision of sharing data which previously had to
  be guessed at

## Changed
- Session started events are now sent after a 3 second delay, to skip
  reporting on accidental sessions and increase the likelihood that
  universal link opens are recorded in the event


1.0.4 - 2015-12-08
==================

First release in a production app!

## Changed
- Renamed delegate methods to add `megacool` prefix

## Fixed
- SDK version can now be found in `Megacool.h`
- Detecting a couple previously ignored error conditions


1.0.3 - 2015-12-07
==================

1.0.2 was never released to the public.

## Added
- A custom iOS7 deep link handler to support the iOS7 initialization signature

## Changed
- Signature for startWithAppConfig have been renamed. It now takes in an event
  handler that takes in generic events and not only deep link events. This is
  where you can react to invites/installs generated.


1.0.1 - 2015-12-06
==================

## Fixed
- A bug that prevented `generated install` events from being sent

## Added
- Documentation: setDelegate in sharedMegacool
- Documentation: Basic failure detection


1.0.0 - 2015-12-01
==================

First release!
