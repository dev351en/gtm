Build the actual deployable JAR only after pulling true Paper 26.3 API with Gradle + JDK 25:
  gradle clean build
Then locate build/libs/SDCraftCore-1.0.0-test.jar and test on a disposable Paper 26.3 server.
The included experimental JAR was produced offline against local fake API compile stubs, never on a Paper runtime. Do NOT treat it as production verified.
