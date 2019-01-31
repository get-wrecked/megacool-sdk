Changelog
=========

The Megacool SDK adheres to [semantic versioning.](http://semver.org)

4.0.5 - 2019-01-31
==================

## Fixed
- iOS: Frames could appear in the recording that was rendered after a call to `pauseRecording` or
  `stopRecording`.
- Android: Sharing to WeChat now respects the sharing strategy, instead of always sending just the
  GIF.


4.0.3 - 2019-01-30
==================

## Fixed
- iOS: Optimize sharing to VK, now includes a GIF.
- iOS: Enable sharing to Sina Weibo.
- Android: Optimize sharing to KakaoTalk. Used to be media only, now does link with still image
  preview by default, and the old behavior if strategy is set to MEDIA.


4.0.2 - 2019-01-25
==================

## Fixed
- Race condition that could cause a crash if a recording was started just after initialization when
  using OpenGL.
- Unity: The default sharing strategy when using the MegacoolShareConfig was accidentally changed
  to MEDIA in 4.0.0, this has been restored to LINK (as the docs claimed it should be).
- Android: When sharing without a recording and without a fallback image, some of the apps you could
  select could hang waiting for content.
- Android: Share destinations that only accept text didn't show up in the share modal.
- Unity Editor: Exception when trying to remove the default recording.
- Unity: Possible exception during GIF preview if a frame failed to load.


4.0.1 - 2019-01-14
==================

## Fixed
- Unity: `MegacoolEvent.Data` was null for `ReceivedShareOpened` events on iOS.


4.0.0 - 2018-12-31
==================

## Changed
- Several methods for setting default values for recording and sharing have been replaced with
  `setDefaultRecordingConfig` and `setDefaultShareConfig`, respectively. This will like earlier be
  merged with the config given directly to the recording and share methods to produce the final
  config for the given action. On iOS we've also moved a couple properties that weren't earlier
  possible to customize on a per-share or per-recording basis like last frame delay, last frame
  overlay, sharing strategy, share message into either `MCLRecordingConfig` or `MCLShareConfig`
  to fix that.
- `forceAdd` has been removed from the recording config. We've added a new `captureFrame` method
  with a third boolean parameter for `forceAdd` in its place.
- The default sharing text has been changed from "No way you'll beat my score" to "Check out
  this game I'm playing!".
- Unity: Some files have been deleted from earlier versions, make sure you delete the following
  files or they might cause compilation errors:
    Assets/Megacool/Plugins/libMegacool-Unity.a
    Assets/Megacool/Scripts/MegacoolFrameCaptureConfig.cs
    Assets/Megacool/Scripts/MegacoolPreviewConfig.cs
    Assets/Megacool/Plugins/include/Megacool/MegacoolUnity.h
- Android: Many static methods on `Megacool` related to recording and sharing including
  `startRecording()`, `stopRecording()`, `captureFrame()`, and the various `share()` and
  `shareTo()` methods have been replaced with instance equivalents. Calling `Megacool.start()`
  now returns an instance, and you can also get an instance by calling `Megacool.getInstance()`.
- Android: The SDK is now compatible with Android API level 16 (used to be 18), but recording is
  still 18+. Below 18 there's only sharing of fallback images available.
- iOS: Default sharing to Kik is now link only, set sharing strategy to Media to revert to the old
  behavior.
- iOS: `MCLSharingStrategy` option "GIF" has been renamed to "Media", as this option will
  prioritize any kind of media, not only GIFs (like fallbacks).
- iOS: `MCLCaptureMethod.kMCLCaptureMethodOpenGL` has been split into
  `MCLCaptureMethod.kMCLCaptureMethodOpenGLES2` and `MCLCaptureMethod.kMCLCaptureMethodOpenGLES3`.
- iOS: The type of `MCLRecordingConfig.frameRate` has been changed from float to int.
- Android: `Megacool.CaptureMethod.OPENGL` has been split into two variants:
  `Megacool.CaptureMethod.OPENGLES2` and `Megacool.CaptureMethod.OPENGLgES3`.
- Android: `OverflowStrategy` has been made an actual enum. This shouldn't require any changes to
  your code as the syntax remains the same.
- Unity: `MegacoolFrameCaptureConfig` has been removed, `CaptureFrame` now takes in the same
  configuration object as `StartRecording`.
- Unity: `MegacoolReferralCode.InviteId` has been renamed to `MegacoolReferralCode.UserId` to be
  consistent with the other platforms.
- Unity: The configuration menu item has been moved to Window/Megacool.
- Unity: `MegacoolGifPreview.GetNumberOfFrames()` now returns the number of frames loaded in the
  preview, use this to sanity check frame counts before showing the preview.
  `Megacool.GetNumberOfFrames()` is available for checking for other non-preview related causes.
- Unity: The type of `MegacoolOverflowStrategy` is changed to enum.
- Unity: The type of `MegacoolShareConfig` and `MegacoolRecordingConfig` has changed from struct to
  class.
- Android: `RecordingConfig.lastFrameOverlayUrl` has been renamed to `lastFrameOverlayAsset()`, to
  clarify that it only works with asset filenames.

## Added
- iOS: Support for sharing gifs to Snapchat.
- Android: You can now call `Megacool.setOnUserIdReceivedListener()` to receive the `userId` once it
  becomes available
- Android and iOS: There is now an additional `Megacool.setCaptureMethod()` method that takes in a
  scale factor as the second parameter. This allows you to customize the scaling performed during
  capture, which may be useful if your UI contains important text elements that were previously
  unreadable with the default scaling. We've also added some documentation to explain our default
  scaling algorithm so you can determine if this is suitable or not for your needs. Note that we
  generally don't recommend using this to produce larger recordings at the moment, as performance is
  likely to suffer with much larger recordings.
- Unity: If you're using a custom Android main activity (anything else than
  `com.unity3d.player.UnityPlayerActivity`), you can now set this in the configuration panel to
  ensure the manifests are merged correctly.

## Removed
- Cropping has been removed from the recording config since it didn't work reliably. On Unity the
  unused `Megacool.Crop` struct was also removed.
- iOS: `Megacool.initCapture` has been removed. You can now just call `Megacool.setCaptureMethod`
  and we'll do the capture initialization for you.
- iOS: `MCLPreviewConfig.includeLastFrameOverlay` has been removed. The previews will now always
  show last frame overlay, if one is set.
- Android: `Megacool.initCapture()` has been removed. If you were calling this, just calling
  `Megacool.setCaptureMethod()` is now enough and we'll handle the capture initialization for you.
- Unity: The keyword arguments to the MegacoolRecordingConfig constructor. Use object initializers
  instead.

## Fixed
- Unity iOS: Fix crash if trying to delete the default recording.
- iOS: `application:openURL:options` now correctly reports  whether the link was handled by Megacool
  or not.
- Android: Recordings are now only scaled down instead of scaled down and cropped.
- Android: The bandwidth for multiple shares of the same media has been reduced
- Android: Several recording methods formerly did disk operations on the main thread, these have
  now been moved to the background.
- Android: Fixed a possible ANR during SDK initialization on some devices.
- Unity: Compiler warning on Unity 2018.1 and newer in MegacoolPrebuild.
- Unity: Updating the SDK no longer overwrites any local changes made to the Android manifest.
- Unity: Error in the Editor when pausing the default recording.

## Deprecated
- Android: `ShareConfig.fallbackImageUrl` have been deprecated in favor of
  `ShareConfig.fallbackImageAsset`, since the former didn't actually support arbitrary urls.


3.3.7 - 2018-11-19
==================

## Changed
- Default sharing to Kik is now link only, set sharing strategy to GIF to revert to the old
  behavior.
- Android: Sharing to Snapchat and Reddit now defaults to link, set sharing strategy to GIF to
  revert to the old behavior.
- Android: Sharing to YouTube now includes the text and link in the video description.

## Added
- iOS: Support for sharing GIFs to Twitter and Snapchat.

## Fixed
- Android: Couldn't return to app after sharing to Snapchat or Facebook Lite.
- Android: Hangouts, Messages and Facebook Lite doesn't show up twice in the share modal anymore.


3.3.6 - 2018-10-24
==================

## Fixed
- Unity: Recording would stop if the MegacoolManager was deactivated and reactivated, like in a
  scene change.
- Recording could end up in a state where no more frames were captured if the device couldn't
  achieve the target capture frame rate.
- If the device wasn't capable of recording at the target frame rate, timelapse recordings
  would lower it's playback frame rate. This is intended for latest and highlight recordings, but
  not timelapses.
- iOS: `pauseRecording` was ignored for timelapse recordings.
- iOS: If `keepCompletedRecordings` was set to true, then later set to false, existing recordings on
  disk wouldn't be cleaned up, only ones recorded after the configuration change.
- iOS: Multiple timelapse recordings after each other with the same `recordingId` would capture
  gradually less and less frames unless `keepCompletedRecordings` was set.
- Android: Removed misleading warning when setting recordingId null through RecordingConfig.


3.3.5 - 2018-09-26
==================

## Fixed
- Android: The `Megacool.shareToX()` methods now _only_ include the packages related to the channel
  you've selected. This was a regression from 3.3.0.
- Unity: Warnings when updating the SDK that the UUIDs for files have changed. You might see the
  warning once when applying this update, but shouldn't see it anymore after that.
- Unity: Incorrect platform markers for libMegacool-Unity.a causing Android builds to fail with
  "Unknown CPU architecture for library".
- Unity: Improve capture reliability for games running at 30fps.
- Android: One more issue was found with getShares from threads without a looper, this should now
  be fully resolved.
- Android: `Megacool.deleteRecording()` will also purge stale data from memory in addition to
  removing it from disk.
- Android: The SDK would not have been correctly initialized on some devices that couldn't encode
  MP4.
- iOS: Explicitly declare external properties as `strong` to avoid warnings in non-ARC projects.
- Android: Out of memory error if a failing method (like `getShares` on a non-looper thread) is
  called repeatedly.

## Deprecated
- Android: All `Megacool.share()` and `Megacool.shareTo*()` methods have been deprecated in favor of
  equivalent variants that take in an `Activity` as the first parameter. This should prevent
  Exceptions that prevent the share modal from appearing on some devices.


3.3.4 - 2018-09-14
==================

## Fixed
- Android: Methods that take callbacks (like `getShares`) that was called from threads without a
  Looper stopped working after the same-thread callback fixes in 3.3.0. We'll run these callbacks
  run from a background thread in these cases (similar to pre-3.3.0 behavior) now. If you would like
  your callbacks to be run on the same thread that you give them to us on, use a `HandlerThread` or
  ensure that the thread has a `Looper`.


3.3.3 - 2018-09-10
==================

## Fixed
- Unity: Target size computation has been improved to prevent very large GIFs on several devices,
  improving performance.
- iOS: Crash if trying to load invalid frame for encoding.
- Events will no longer be attempted delivered while the app is buing put in the background,
  increasing the reliability of the sentShareOpened event.


3.3.2 - 2018-08-29
==================

## Fixed
- Unity: Events on Android had the wrong type, everything was classified as receivedShareOpened.
  This bug was introduced in 3.3.0.
- Android: Event sending and notification retrieval are more reliable now.
- Android: `getPreviewData` would return an empty frame set if the last frame failed to decode when
  trying to apply a lastFrameOverlay.
- Android: Completed recordings were deleted when the app shutdown even if `keepCompletedRecordings`
  was enabled.


3.3.1 - 2018-08-21
==================

## Fixed
- Unity: Actually set SharingStrategy on Android.
- Android: Improved the sharing experience to Line and Viber.


3.3.0 - 2018-08-20
==================

The automatic frame rate adjustment changes we introduced in 3.2 caused devices that couldn't
capture at the intended frame rate (usually 10fps) to play back the content at the frame rate they
actually managed, like 8. This caused recordings to be quite choppy, whereas earlier this had been
camouflaged by them always being played back at the intended rate, like 10fps, and thus getting a
slight speedup. To try to keep recordings smooth in most cases we're now defaulting to speeding them
up a little bit to get back the old behavior.

## Changed
- If you haven't set an explicit playback framerate we will now default to 20% speedup from the
  capture frame rate. This prevents devices that can't capture at higher frame rates from getting
  choppy recordings, but can of course be overridden by setting an explicit playback framerate.
- Unity iOS: Previews now includes the last frame overlay, if set.
- iOS: Roll back to send gifs instead of video for Messages, for better quality when sent as MMS.

## Added
- Android: You can now use `Megacool.setSharingStrategy` to choose whether gifs or links should be
  prioritized for channels that support either, but not both at the same time. This is the same as
  iOS has had for some time, and defaults to prioritize links.

## Fixed
- Native crash if some initialization methods are called out of order.
- Android: Any callbacks (with the exception of the ShareFilter) you give to us are now run on the
  same thread you create them on.
- iOS: The recording was missing if sharing the same recording twice with `presentShareToMessages`.
- Android: Retry failed http requests faster if it's for a request that might cause
  `receivedShareOpened` events to be received.
- Android: Calls to `Megacool.share()` are now debounced to prevent multiple taps from creating
  multiple share prompts.

## Removed
- Android: The deprecated ShareConfig.Builder class, construct a ShareConfig directly instead.
- Android: The deprecated LinkClickedActivity. Add the Megacool intent-filters to your main activity
  instead.

## Deprecated
- iOS: The `includeLastFrameOverlay` option in `MCLPreviewConfig` is now deprecated.


3.2.1 - 2018-07-17
==================

## Fixed
- Android: Fix a crash during initialization of the native libraries we use. The SDK will operate
  in a degraded state where recording doesn't work if this happens, but sharing and referrals work
  as normal.
- iOS: Remove misleading log message about missing config if `continueUserActivity:` is called
  before `startWithAppConfig:`, which often happens under Unity under normal circumstances.
- Android: Prevent creation of multiple link clicked events when switching between recent apps.
- Android: Sharing to Discord previously wouldn't allow the user to return to the game unless they
  force-closed the app. This is a bug in Discord, but we added a workaround that enables getting
  back to the app through the task manager.


3.2.0 - 2018-06-26
==================

## Changed
- GIF playback speeds are now adjusted according to the capture framerate that the device
  is capable of recording at, preventing slower devices from getting sped-up recordings.
- iOS: The default sharing strategy is now links. Set
  `[Megacool sharedMegacool].sharingStrategy = kMCLSharingStrategyGif` if you want the old behavior.

## Deprecated
- Android: The `LinkClickedActivity` has been deprecated. Please use your own Activity to handle
  intents with the `android.intent.action.VIEW` action (such as the MainActivity). See the
  quickstart guide or the documentation for `co.megacool.megacool.LinkClickedActivity` for details.

## Fixed
- Less bandwidth usage due to uploading mp4 instead of gifs.
- Less bandwidth usage on multiple shares by only uploading media file once.
- Android: Moved some disk operations that could have caused UI jank off the main thread.
- Android: GIF creation would stop entirely if the last frame errored for some reason when using the
  dynamic color table, instead of ignoring the frame as it should.
- Android: Fix potential native code crash when reading captured frame data.
- iOS: Linker error on iOS7 Unity apps.
- iOS: Improve the sharing experience to Discord, Kik, Hangouts, Telegram, Yahoo Mail and Zalo.
- Unity iOS: No longer shares gif fallback as still images.

## Removed
- Android: The deprecated `Share()` constructors have been removed. To set a custom url or add extra
  parameters to shares, please use the `ShareConfig()` class instead.
- iOS: Removed deprecated `MCLShare` constructors.
- iOS: Removed deprecated `MCLShare *share` property from the `MCLShareConfig` class.
- iOS: Removed deprecated `handleEventsForBackgroundURLSession:completionHandler:` method from
  `Megacool`.
- iOS: Removed deprecated `continueUserActivity:` method from `Megacool`.
- Unity: The deprecated `Start(Action<MegacoolEvent> eventHandler)` initializer has been removed.
- Unity: The deprecated `Share(Url, Data)` constructors have been removed. Set these properties on
  the ShareConfig instead. The `ShareConfig.Share` property has also been removed.
- Unity: The deprecated `ShareConfig.LastFrameOverlay` property has been removed, set this on the
  Megacool instance instead.
- Unity Android: MegacoolUnityDeepLink activity has been removed. If you manually manage your
  manifest merging, please see our Android Quickstart guide for details on how to update your
  AndroidManifest.xml file.


3.1.9 - 2018-05-22
==================

## Fixed
- Unity: iOS crashing with DllNotFoundException when calling `GetNumberOfFrames`.


3.1.8 - 2018-05-02
==================

## Changed
- Android: `Megacool.setShareListener` has been made available for all API levels, and the
  `didPossiblyCompleteShare` callback will always be called on API level 22 and below where we can't
  detect anything more specific. This also affects Unity's `PossiblyCompletedSharing` delegate.

## Fixed
- iOS: GIFs would not get uploaded when sharing a recording more than once.
- Android: Link clicks are handled even if the app is already open.
- Android: A race condition in which the GIF file might be deleted before a share is completed when
  the network fails.
- Android: NullPointerException if `keepCompletedRecordings` or `sharingText` is attempted set
  before `start()` is called.


3.1.7 - 2018-04-18
==================

## Fixed
- Weak sanity check would discard frames with fully black bottom rows.
- Android: Handling link clicks with the `LinkClickedActivity` no longer gets stuck on an empty
  screen if the app was already opened.
- Unity iOS: NullPointerException if calling any of the `Share*` methods with a ShareConfig that
  didn't have both Data and Url set on some Unity versions.

## Added
- iOS: `[Megacool sharedMegacool].sharingStrategy` now enables setting whether GIFs or links should
  be shared to channels that only support one of them. The default is GIF, which is the same as
  we've done so far. Set this to `kMCLSharingStrategyLink` to prioritize links, needed if you want
  referrals. Currently only affects WhatsApp.
- Unity: Added `Megacool.Instance.SharingStrategy` to wrap the iOS sharing strategy (see above).
  Setting this has no effect on other platforms.


3.1.6 - 2018-04-11
==================

## Fixed
- Android: GIFs are no longer copied multiple times when they fail to be uploaded.
- Android: If share uploads fail they are now discarded instead of being retried forever.
- Unity: Accept 0 as a valid `lastFrameDelay` value, like the native SDKs.
- iOS: Stop ignoring fallback images and last frame overlays *with* a `file://` prefix.
  Introduced in 3.1.5.


3.1.5 - 2018-04-03
==================

## Fixed
- Android: A race condition in link click handling could prevent some installations from being
  detected.
- Unity/iOS: Fallback images and last frame overlays set from Unity or set by a NSURL without a
  file:// prefix was ignored.
- Unity: Only check config keys if build target is iOS or Android.
- Restored Unity Editor recordings, this broke in 3.1.4.


3.1.4 - 2018-03-16
==================

## Fixed
- Android: GIF previews missing if some frames failed to load.
- Unity: Frames would occasionally get corrupted when using `MegacoolCaptureMethod.BLIT` or
  `MegacoolCaptureMethod.RENDER`.
- Unity iOS: Memory leak while starting previews or getting the share text.
- Unity iOS: Occasionally missing previews due to bad memory management. Introduced in 3.0.0.
- Android: Multiple share modals no longer show up when rotating the device during a share.
- Unity: Calling `MegacoolGifPreview.StartPreview()` with a preview already playing would cause it
  to stop and hide the preview, instead of starting a new preview. Repeated calls to StartPreview
  would also not start a new preview until StopPreview was called.
- Unity: Previews would only show the last frame if frames failed to load at the target framerate,
  instead of doing a best-effort rendering.
- Unity: The last frame delay in the preview was one preview frame duration longer than it should
  have been.


3.1.3 - 2018-03-03
==================

## Fixed
- Android: Crash on older devices due to an invalid date format. Introduced in 3.1.1.
- Unity iOS: Severe memory leak on ES2 devices due to an attempted fix for ES2 SCREEN capture
  introduced in 3.1.0.
- Unity Editor: ArgumentNullException when `Megacool.Instance.StartRecording` is called with a null
  recordingId successively.


3.1.2 - 2018-02-28
==================

## Fixed
- Fix a race condition that could make capture stop working. This bug was introduced in 3.1.1.
- Android: Fixed bug causing the share modal window to not be displayed in `Megacool.share()`, this
  was introduced in 3.1.0.


3.1.1 - 2018-02-27
==================

## Fixed
- Frames could bleed across recordings under Unity or custom engines.
- When using the highlight recording the highlight was not positioned correctly if less than
  maxFrames frames had happened since the highlight.
- Unity: Excessive logging, particularly when running in the Editor.
- Unity: Memory leak while recording from the Editor.
- Unity: Default recording configuration set on the Megacool.Instance was not respected in the
  Editor.
- Android: Fixed bug causing custom share data to be ignored by the server due to missing date
  information.
- Android: Prevent potential crashes when opening the app from a referral.


3.1.0 - 2018-02-16
==================

## Changed
- Android: Listeners and callbacks that you set are no longer guarded by our RuntimeException
  guards, so you will now need to catch these yourself. This includes ShareListener, ShareCallback,
  ShareFilter, and OnEventsReceivedListener.
- iOS: If you're using Swift the added nullability annotations means you might have to remove some
  optional markers.

## Fixed
- Slow share modal popup on both platforms. This has been made async, so on low-end devices it's
  still possible the user will have to wait for the gif creation to finish if they are very fast
  to select a share channel and the device is very slow.
- Android: GIF color quality has gotten significantly better, comparable to what was available on
  iOS using the AnalyzeFirst color table. The default now uses the new color table, but the old
  behavior is available by setting `Megacool.setGifColorTable(GifColorTable.FIXED)`.
- Android: When running under OpenGL ES2 some failure modes weren't detected properly and resulted
  in black frames in the preview and GIF.
- Android: Track share channels on newer devices like we do on iOS.
- Android: Recordings are now automatically paused if a share is initiated.
- Android: Close leaked connections when submitting debug data.
- Unity: `MegacoolCaptureMethod.SCREEN` was never used when using OpenGL ES2, even though it often
  works.

## Added
- Unity: Support for recording and previewing GIFs in the editor.
- iOS: A new color table option kMCLGIFColorTableDynamic, which performs roughly like AnalyzeFirst,
  but is also available on Android.
- iOS: Nullability annotations.
- Android: Share callbacks are now available as on iOS and Unity. See the docs for the
  `Megacool#ShareListener` for details.
- Android: `GifColorTable/Megacool.setGifColorTable()` can be used to customize the colors in the
  GIFs created.

## Deprecated
- iOS: The `MCLShare` constructors were supposed to have been deprecated in 3.0.0, fixed now.


3.0.2 - 2018-02-01
==================

## Fixed
- Android: Don't trigger `LINK_CLICKED` events for unrelated referrers from the Play Store.


3.0.1 - 2018-01-17
==================

## Fixed
- Android: Race condition that could crash the app if some Android callbacks were called before the
  SDK was fully initialized (introduced in 3.0.0).
- Unity: Set PostProcessBuildAttribute to 1000 to prevent clash with other plugins.


3.0.0 - 2018-01-10
==================

Mostly cleanup and bug fixes, but bumping the major version since iOS has gotten some
backwards-incompatible changes. All the major iOS methods (startRecording, preview, share) now
take configuration blocks instead of dictionaries, ensuring much less magic keys and more type
safety.

## Changed

- Android: *You must now call `.destroy()` on GifImageViews* to avoid a memory leak.
- `deleteRecording` now accepts nil/null to delete the default recording.
- iOS: All recording and share methods now accept a configuration block instead of a dictionary,
  receiving the new MCLRecordingConfig and MCLShareConfig objects.
- iOS: The kMCLFeature and kMCLGIFColorTable types have been renamed without the k prefix (the
  values are unchanged).
- Android: Moved `GifImageView` from `co.megacool.megacool.widget` package to `co.megacool.megacool`
  package.
- Android: `lastFrameOverlay` moved from ShareConfig to `Megacool.setLastFrameOverlay`. This did
  not go through the normal deprecation cycle since it wasn't widely used.
- Android: Deep links are now automatically extracted even if you don't use the LinkClickedActivity,
  thus you can move the Megacool `<intent-filter>`s to your main activity to save an extra activity
  on startup.
- Unity: The SDK will now warn if trying to build with an Android min API level lower than what is
  supported by the SDK, and help setting it when opening the configuration in the Editor.

## Deprecated
- Passing a Share in the share configuration has been deprecated in favor of setting the url and
  data directly.
- Android: `ShareConfig.build()` has been deprecated in favor of `new ShareConfig()`.

## Added
- Get number of frames captured so far for a recording with `getNumberOfFrames`/`GetNumberOfFrames`.
- iOS: MCLRecordingConfig and MCLShareConfig configuration objects.
- iOS: Last frame overlay can now also be set by URL to an image on disk, with
  `Megacool.lastFrameOverlayUrl`.
- Android: If the `ACCESS_NETWORK_STATE` permission is granted network requests are retried faster,
  but the permission is not required.
- Android: lastFrameOverlay for gif previews and shares.
- Android: Nullability annotations.
- Unity: Last frame overlay support for Android.
- Unity: NGUI support for gif previews.
- Unity: Configure shared URL and associated data with .Url and .Data on MegacoolShareConfig.

## Fixed
- Android: Network requests like GIF uploads have been made more reliable, these are now
  automatically retried later if the network is unavailable.
- Android: GIF previews load one frame at a time to reduce memory consumption.
- Android: Crash if trying to share from an app with a name that is not filesystem safe.
- Unity: Reduced number of allocations during coroutine yields.

## Removed
- iOS: The `kMCLConfig*` constants have been removed in favor of dedicated configuration classes.
- iOS: The deprecated methods `renderPreview` and `renderPreviewWithConfig` (deprecated since 2.5)
  has been removed. Use `getPreview` instead.
- iOS: Last frame overlay can no longer be configured in the `presentShare*` config dicts.
  Per-recording overlays will probably be added to the recording config later though, in the
  meantime you can set a default one with `Megacool.lastFrameOverlay`.


2.6.5 - 2017-12-16
==================

## Fixed
- A sanity check for valid frames during capture was broken, letting black frames into the GIF and
  preview instead of skipping them.


2.6.4 - 2017-12-13
==================

## Fixed
- Android: No more allocations during capture!
- iOS: Support for sharing GIF, link and text to KakaoTalk and Line.
- iOS: Include image when sharing to Twitter with the default share, instead of only a text and
  link.


2.6.3 - 2017-12-06
==================

## Fixed
- Race condition that could allow extra frames to be added after pause/stop.
- Memory leak when creating GIFs. For iOS this would only manifest if using the fixed color table.
- Unity: Fix missing initialization of GifPreview if added in the same frame it's enabled.
- iOS: Reduce peak memory usage when creating GIFs.


2.6.2 - 2017-12-01
==================

## Fixed
- Android: Memory leak when the desired framerate is higher than what we can achieve on the device.
- Android: Memory leak during capture.
- Android: NullPointerException if calling captureFrame without a config.
- Android: Drastically reduce the number of Java allocations made during capture.
- Unity: Race condition that could cause us to gradually stop capturing new frames.


2.6.1 - 2017-11-16
==================

## Deprecated
- iOS: The instance methods of `continueUserActivity` and
  `handleEventsForBackgroundURLSession:completionHandler` have been replaced with class methods,
  to prevent a race condition if these were called before start(), causing universal link clicks to
  not be noticed by the SDK. If you use the `MEGACOOL_DEFAULT_LINK_HANDLERS` macro you don't have to
  do anything, otherwise you should change
  `[[Megacool sharedMegacool] continueUserActivity:userActivity]` to
  `[Megacool continueUserActivity:userActivity]` (and similarly for
  `handleEventsForBackgroundURLSession`). The new `handleEventsForBackgroundURLSession` now also
  returns a BOOL indicating whether we actually handled the events, or whether they should be passed
  on to another handler.

## Fixed
- Unity Android: Stopped Proguard from complaining if building with gradle.
- Unity: Ambiguity between current and deprecated `Start` methods.
- Unity: Regression since 2.5.0 causing builds to fail on Unity 5.3. The fix included re-creating
  the prefabs, which might break links to the old prefabs - make sure these are set correctly after
  updating.
- Unity: Crash if stopping preview before any frames have been loaded.
- Unity: MegacoolLinkClickedEvents were not triggered for iOS universal links unless the app was
  already running. The app would open correctly, but a lot of re-engagements would not have been
  tracked correctly because of this.
- Unity: Crash if clicking links where the share is missing.


2.6.0 - 2017-11-03
==================

Very exciting release this time, introducing both highlight recording and capture without extra
blits or renders on Unity.

## Added
- Added a new `highlightRecording` feature which enables recording the best parts of the gameplay,
  in addition to the existing latest and timelapse strategies. Read more in
  [the quickstart](https://docs.megacool.co/quickstart#b-highlight-recording).
- Unity: You can now more easily customize the recording by explicitly attaching the MegacoolManager
  to a camera in the scene, enabling you to keep hide UI elements or show overlays only to this
  camera.
- Unity: `OnReceivedShareOpened(megacoolEvent)` that gets called when a Megacool share is opened on
  your device
- Unity: `OnLinkClicked(megacoolEvent)` that gets called when your shared link is clicked
- Unity: `OnSentShareOpened(megacoolEvent)` that gets called when your Megacool share is opened
- Unity: `OnMegacoolEvents(List)` that gets called with all events at once
- iOS: Copy GIF to pasteboard button in the UIActivityViewController
- Android: Added an HTML version of the sharing intent text for apps that support it.
- Android: Fallback images when GIFs are unavailable, similar to iOS (this has been available
  through `ShareConfig` for some time already, but was very buggy and didn't work from Unity).
- Android: forceAdd for timelapse recordings, similar to iOS.
- Android (and Unity Android): Custom share buttons! Similar to what you can do on iOS you can now
  target a specific app with a dedicated button. We've added support for the same channels as on
  iOS: SMS, Mail, Facebook Messenger and Twitter. Call `shareToMessenger()`, `shareToMail()` etc
  instead of the regular `share()` to use this.

## Changed
- Unity: You should no longer manually add the `MegacoolManager` to the scene, the prefab has been
  removed and recording will magically work without it.
- Unity: Recording has been rewritten to not require blitting or rendering a texture from Unity on
  OpenGL ES3 apps, meaning higher performance capturing that is identical to what is shown on
  screen. This automatically falls back to capturing via a texture on ES2 or Metal.
- Unity: `Start(Action e)` is now deprecated. Use `Start()` and add callbacks to their respective
  delegates.

## Fixed
- Unity: `MegacoolShareConfig` has been formatted to support fallback images on Android.
- Unity: Recording on apps with multithreaded rendering has been fixed.
- iOS: Crash if trying to set `keepCompletedRecordings` or `disableFeatures` while debug mode is on.
- iOS: Crash if trying to send debug data before a recording has been started.
- iOS: Sharing to Slack now makes the link clickable
- iOS: The custom Twitter share now works again by copying the GIF to the pasteboard, opening
  Twitter and letting the user paste the GIF.
- Android: `SharingManager#share()` now runs mostly on a background thread to prevent
  blocking the UI while the GIF is created.
- Android: Setting last frame delay to 0 means the same as on iOS - the same delay as the other
  frames.
- Android: `resetIdentity()` was ignored if called after `start()`, but crashed if called before.
  The crash has been fixed, this should still be called before `start()`.
- Android: A race condition caused most state updates during timelapse capture from being persisted,
  ensuring that hardly any frames were captured.
- Android: Shares was sometimes not created correctly if network requests happened in a certain
  order.


2.5.1 - 2017-09-12
==================

## Fixed
- iOS: Removed some debug logging when sharing.
- Android: String resources are now marked as untranslatable to avoid lint errors.
- Android: Deep links from Unity could cause an exception to be printed and the link to be ignored.
- Android: `share()` now continues sharing just text and link if the GIF for some reason fails.
- Unity: The Megacool.Instance.SharingText getter is now actually implemented and doesn't crash.
- Unity: String resources are now marked as untranslatable to avoid lint errors.

## Added
- iOS: Missing getters for `Megacool.maxFrames` and `Megacool.frameRate`.


2.5.0 - 2017-08-23
==================

## Changed
- Unity: The `MegacoolGifPreview` has been remade as a pure Unity prefab, enabling it to be freely
  positioned and animated in Unity. Just replace the old one and be sure to connect it to your
  script in the inspector (drag and drop).
- Unity: Scheme has been split to accomodate different schemes between iOS and Android. If you had
  an existing scheme you have to enter it again for the relevant platform(s).
- Android: `enableDebugging` has been renamed to `setDebug` for parity with iOS and Unity.

## Fixed
- iOS: Last frame delay in previews was not respected unless a last frame overlay was set.
- iOS: GIFs created with a fixed color table did not loop on some channels.
- Android: Setting last frame delay to 0 means the same as on iOS - the same delay as the other
  frames.
- Android: GIFs did not loop on some channels.

## Added
- Unity: A predefined canvas named `MegacoolPreviewCanvas` that contains the `MegacoolGifPreview`.
  This can be added directly to the scene so you don't have to add a UI canvas first.
- iOS: `getPreview` has been added as a more performant alternative to `renderPreviewOfGif`. This
  returns a `MCLPreview` instead of a `UIImageView`, but it's a subclass of `UIView` so should be
  easy to drop in as a replacement for `renderPreviewOfGif`.

## Removed
- iOS: The deprecated methods `handleDeepLink` and `openShareModalIn:` that was supposed to be
  removed in 2.3.0 have finally been removed.

## Deprecated
- iOS: `renderPreviewOfGif` and `renderPreviewOfGifWithConfig:` have been deprecated in favor of
  `getPreview`, which is easier to configure and performs better.


2.4.5 - 2017-08-14
==================

## Fixed
- Unity: Compile error when building to iOS.


2.4.4 - 2017-08-10
==================

## Fixed
- Android: Crash when calling `startRecording` due to a threading issue introduced in 2.4.3.


2.4.3 - 2017-08-09
==================

## Fixed
- Unity: Facebook logins broken because of a `openUrl` conflict.
- Unity: Severe performance hit on certain devices due to using `Graphics.Blit`.
- Unity: `SubmitDebugData` and `Megacool.Debug = true` now also works for Android.
- Android: All SDK entrypoints have been guarded against RuntimeExceptions to prevent crashing apps
  on errors, barring any crashes in native code. Stacktraces from RuntimeExceptions are also
  automatically reported to us so that they'll be fixed ASAP.
- Android: NullPointerException if trying to authenticate with the API with incorrect local time on
  device.

## Removed
- Unity: `MegacoolRecordingConfig.Crop` and `MegacoolFrameCaptureConfig.Crop`, since they don't work
  yet. Will come back soon.

## Added
- Android: `submitDebugData` similar to on iOS. If the SDK is not giving you the results you
  expected, call `Megacool.enableDebugging()` at the beginning of the session, and call
  `Megacool.submitDebugData("expected X but got Y")` after observing the strange behavior, and we'll
  take a look.


2.4.2 - 2017-07-14
==================

## Fixed
- iOS: Previews now run with a black background, to hide the actual background in case of transparency
  in the frames.
- Android: Race condition between `captureFrame()` and `pause()` could cause one extra frame to be included
  in the GIF after a recording had been stopped or paused.
- Unity: The warning for invisible previews have been removed for Unity versions 5.6.2 and above, as it has
  been fixed in newer versions.


2.4.1 - 2017-07-11
==================

## Fixed
- Unity: Building to iOS without selecting universal linking didn't work.
- iOS: Last frame delay was wrong for GIFs created with color table set by analyzing the first
  frame.
- iOS: If last frame delay was set to 0 when using the fixed color table the actual last frame
  duration would be set to `playbackFrameRate`, not `1/playbackFrameRate` as was done when using
  analyze first frame. This behavior is now also documented.
- URLs from other SDKs are no longer submitted to the API in full form, these are now redacted.
  Link clicked events in the event handler will still receive them though, you should sanity check
  these before using them for navigation.


2.4.0 - 2017-06-07
==================

It's here! The latest and greatest, out of RC and ready for the world, the first finished release
that supports compiling to Android from Unity!

Android is still not at full feature parity with iOS, the following is still unimplemented:
- Cropping
- Last frame overlays (last frame delay works however)
- Custom share buttons
- Share analytics, we currently don't track shares completed, so the numbers on the dashboard will
  not be entirely accurate. Re-engaged sessions and installs work though.
- GIF previews currently doesn't work with Unity 5.6. This is a known Unity issue, we are
currently contemplating whether to wait for Unity to fix it or work around it, let us know if
this is a deal breaker for you and we'll speed up a fix.
- Share fallback images

These features will appear gradually as we get around to implementing them, if you've got a crush on
any of them, let us know and we can prioritize that.

## Changed
- Unity: Moved Android manifest. To get deep links working properly on Unity we need to write to
  the main application manifest at `Assets/Plugins/Android/AndroidManifest.xml`, where we in the RC
  wrote to our package-specific manifest at `Assets/Plugins/Android/*Megacool*/AndroidManifest.xml`.
  If you have the old file from the RC, delete that and click "Write Android manifest" again. If you
  already have a custom main manifest it'll get overwritten when you write the Megacool manifest --
  you'll have to merge these manually after the Megacool changes are written. Let us know if you
  bump into any issues with this and we'd be happy to assist, and similarly let us know if there's
  anything we can do to make this easier for you.
- Unity: The unit for last frame delay has been changed from seconds to milliseconds, you probably
  have to update your MegacoolConfiguration accordingly.
- Android: Recording.Config has been replaced by RecordingConfig, which should
  make it much easier to customize recordings.
- Android: Last frame delay was interpreted as seconds, while being documented as milliseconds. It
  is now interpreted as the latter.
- Android: Recordings are now automatically paused when the app is backgrounded, but you have to
  start it again manually when the session is resumed.
- iOS: Last frame delay is now given in ms. The defaults are still the same, but if you use a custom
  last frame delay, multiply that by 1000 to keep the same delay.

## Fixed
- Unity couldn't build to Android with Gradle on Unity 5.5 and lower.
- Android: Broken timelapse recording. Timelapse now works with startRecording, but is still broken
  with captureFrame.
- Android: Repeated shares in the same session not creating GIFs.
- iOS: Occasional crash when rendering previews, introduced in 2.2.0.

## Added
- Unity: Max frames, last frame delay and overflow strategy can now be set for each recording in addition
  to the global defaults. Previously only some of the recording configuration could be set per
  recording.
- Android: `Event.getUrl()` helper to get the URL for link clicked events.
- Android: `Event.getReferralCode()` helper to get the referral code for events.


2.4.0-rc3 - 2017-05-23
======================

2.4.0 getting closer! A couple of issues found so far in the RC that we're aware of:

Android:
- Some people have reported that shares and previews only work the first time in a session, and
that subsequent attempts fail to yield any results. This will be resolved before we release
2.4.0.
- Share analytics is not finished, we currently don't track shares completed, so the numbers on
the dashboard will not be entirely accurate. Re-engaged sessions and installs work though.

Unity Android:
- Deep links in to Unity apps doesn't fully open the app, leading to a blank white screen after
clicking links. This will be resolved before we release 2.4.0.
- GIF previews currently doesn't work with Unity 5.6. This is a known Unity issue, we are
currently contemplating whether to wait for Unity to fix it or work around it, let us know if
this is a deal breaker for you and we'll speed up a fix.


## Changed
- Android: Share, ShareConfig and ShareState have been moved from co.megacool.megacool.share to
  co.megacool.megacool.
- Android: Recording and OverflowStrategy have been moved from co.megacool.megacool.recording to
  co.megacool.megacool.
- Android: Minimum version has been bumped to 4.3 (SDK level 18), to prevent a crash on 4.2.2
  devices.
- Unity: GIF resolution was lowered on iPads for faster processing.

## Fixed
- Unity: Editor crashed if the Megacool configuration inspector was open during build.


2.4.0-rc2 - 2017-05-12
======================

## Changed
- Unity: The `co.Megacool` namespace has been removed and all classes have been renamed with a `Megacool`
  prefix for consistency. If you had a `GifPreview` in your scene this will loose the script
  reference, attach the new `MegacoolGifPreview` instead.

## Fixed
- Unity: Crash on launch with `Unable to get provider android.support.v4.content.FileProvider`.
- Android and Unity Android: `RECEIVED_SHARE_OPENED` events not being fired.


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
