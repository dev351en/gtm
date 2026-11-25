plugins { java }

group = "com.sdcraft"
version = "1.0.4-r4-repair"

repositories {
    mavenCentral()
    maven("https://repo.papermc.io/repository/maven-public/")
}

val preservedCore = file("../runtime/functional-r4/plugins/SDCraftCore-1.0.3-r4-functional-candidate.jar")
val patcher = sourceSets.create("patcher") { java.srcDir("tools") }
dependencies {
    add(patcher.implementationConfigurationName, "org.ow2.asm:asm:9.8")
    compileOnly(files(preservedCore, "../plugins/VaultUnlocked-2.20.3.jar"))
    compileOnly("io.papermc.paper:paper-api:26.3.build.255-stable")
    testImplementation(files(preservedCore, "../plugins/VaultUnlocked-2.20.3.jar"))
    testImplementation("io.papermc.paper:paper-api:26.3.build.255-stable")
    testImplementation(platform("org.junit:junit-bom:5.11.4"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}
java { toolchain { languageVersion.set(JavaLanguageVersion.of(25)) } }
tasks.withType<JavaCompile>().configureEach { options.encoding = "UTF-8" }
tasks.test { useJUnitPlatform() }
tasks.jar {
    archiveBaseName.set("GTM-Repair-Classes")
    // This is an overlay input, never an independently loadable server plugin.
    archiveClassifier.set("overlay")
}
val patchOutput = layout.buildDirectory.dir("vehicle-patch")
tasks.register<JavaExec>("patchVehicle") {
    dependsOn(patcher.classesTaskName)
    classpath = patcher.runtimeClasspath
    mainClass.set("PatchVehicleBytecode")
    args(preservedCore.absolutePath, patchOutput.get().asFile.absolutePath)
}
tasks.register<JavaExec>("patcherChecks") {
    dependsOn(patcher.classesTaskName)
    classpath = patcher.runtimeClasspath
    mainClass.set("PatchVehicleBytecodeChecks")
    args(preservedCore.absolutePath)
}
tasks.register<JavaExec>("equipmentCompatibilityChecks") {
    dependsOn(tasks.testClasses)
    classpath = sourceSets.test.get().runtimeClasspath
    mainClass.set("com.sdcraft.core.equipment.EquipmentCompatibilityChecks")
    args(preservedCore.absolutePath)
}
tasks.check { dependsOn("patcherChecks", "equipmentCompatibilityChecks") }
