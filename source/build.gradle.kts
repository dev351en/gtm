plugins {
    java
}

group = "com.sdcraft"
version = "1.0.1-r4-candidate"

repositories {
    mavenCentral()
    maven("https://repo.papermc.io/repository/maven-public/")
    maven("https://repo.codemc.io/repository/creatorfromhell/") {
        content { includeGroup("net.milkbowl.vault") }
    }
}

val localVault = file("../plugins/VaultUnlocked-2.20.3.jar")

dependencies {
    compileOnly("io.papermc.paper:paper-api:26.3.build.255-stable")
    // Citizens is an optional runtime integration accessed reflectively by NpcService.
    // Its API is not referenced by compiled sources and must not block this build.
    if (localVault.isFile) compileOnly(files(localVault))
    else compileOnly("net.milkbowl.vault:VaultUnlockedAPI:2.20")

    testImplementation(platform("org.junit:junit-bom:5.11.4"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
    testImplementation("io.papermc.paper:paper-api:26.3.build.255-stable")
    if (localVault.isFile) testImplementation(files(localVault))
    else testImplementation("net.milkbowl.vault:VaultUnlockedAPI:2.20")
}

java {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(25))
    }
}

tasks.withType<JavaCompile>().configureEach {
    options.encoding = "UTF-8"
}

tasks.test {
    useJUnitPlatform()
    testLogging {
        events("passed", "skipped", "failed")
    }
}

tasks.jar {
    archiveBaseName.set("SDCraftCore")
    archiveClassifier.set("")
    archiveVersion.set(project.version.toString())
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
}

// Explicit smoke suites are executable Java mains, not JUnit test classes.
tasks.register<JavaExec>("foundationChecks") {
    dependsOn(tasks.testClasses)
    classpath = sourceSets.test.get().runtimeClasspath
    mainClass.set("com.sdcraft.core.gtm.FoundationChecks")
}
tasks.register<JavaExec>("civicChecks") {
    dependsOn(tasks.testClasses)
    classpath = sourceSets.test.get().runtimeClasspath
    mainClass.set("com.sdcraft.core.gtm.CivicChecks")
}
tasks.check {
    dependsOn("foundationChecks", "civicChecks")
}

tasks.register<JavaExec>("infrastructureChecks") {
    dependsOn(tasks.testClasses)
    classpath = sourceSets.test.get().runtimeClasspath
    mainClass.set("com.sdcraft.core.gtm.InfrastructureChecks")
}
tasks.check { dependsOn("infrastructureChecks") }

tasks.register<JavaExec>("nearMissChecks") {
    dependsOn(tasks.testClasses)
    classpath = sourceSets.test.get().runtimeClasspath
    mainClass.set("com.sdcraft.core.gtm.NearMissChecks")
}
tasks.check { dependsOn("nearMissChecks") }
