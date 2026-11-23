plugins {
    java
}

group = "com.sdcraft"
version = "1.0.0"

repositories {
    mavenCentral()
    maven("https://repo.papermc.io/repository/maven-public/")
    maven("https://maven.citizensnpcs.co/repo")
}

dependencies {
    compileOnly("io.papermc.paper:paper-api:26.3.build.255-stable")
    compileOnly("net.citizensnpcs:citizensapi:2.0.44-SNAPSHOT")
    compileOnly(files("../plugins/VaultUnlocked-2.20.3.jar"))

    testImplementation(platform("org.junit:junit-bom:5.11.4"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
    testImplementation("io.papermc.paper:paper-api:26.3.build.255-stable")
    testImplementation(files("../plugins/VaultUnlocked-2.20.3.jar"))
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
    archiveVersion.set("1.0.0")
    duplicatesStrategy = DuplicatesStrategy.EXCLUDE
}
