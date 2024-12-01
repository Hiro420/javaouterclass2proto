package cock.grasscutters.DumpDescriptorsPlugin.commands;

import java.io.File;
import java.io.FileOutputStream;
import java.lang.reflect.Method;
import java.util.List;
import java.util.Set;

import org.reflections.Reflections;
import org.reflections.scanners.SubTypesScanner;
import org.reflections.util.ClasspathHelper;
import org.reflections.util.ConfigurationBuilder;

import com.google.protobuf.DescriptorProtos.FileDescriptorProto;
import com.google.protobuf.Descriptors.FileDescriptor;

import emu.grasscutter.Grasscutter;
import emu.grasscutter.command.Command;
import emu.grasscutter.command.CommandHandler;
import emu.grasscutter.game.player.Player;

@Command(
        label = "dumpdescriptors",
        permission = "server.dumpdescriptors",
        targetRequirement = Command.TargetRequirement.NONE)
public final class DumpDescriptorsCommand implements CommandHandler {

    @Override
    public void execute(Player sender, Player targetPlayer, List<String> args) {
        try {
            String outputDir = "proto_descriptors";
            File directory = new File(outputDir);
            if (!directory.exists()) {
                directory.mkdirs();
            }

            Reflections reflections = new Reflections(new ConfigurationBuilder()
                    .setUrls(ClasspathHelper.forPackage("emu.grasscutter.net.proto"))
                    .setScanners(new SubTypesScanner(false)));

            Set<Class<?>> classes = reflections.getSubTypesOf(Object.class);

            for (Class<?> clazz : classes) {

                try {
                    String simpleName;
                    try {
                        simpleName = clazz.getSimpleName();
                    } catch (Throwable t) {
                        continue;
                    }

                    if (!simpleName.endsWith("OuterClass")) {
                        continue;
                    }
                    Grasscutter.getLogger().info("Dumping " + simpleName + " descriptor...");

                    Method getDescriptorMethod = clazz.getMethod("getDescriptor");

                    FileDescriptor fileDescriptor = (FileDescriptor) getDescriptorMethod.invoke(null);

                    FileDescriptorProto fileDescriptorProto = fileDescriptor.toProto();

                    String outputPath = outputDir + File.separator + simpleName + ".proto.pb";

                    try (FileOutputStream outputStream = new FileOutputStream(outputPath)) {
                        fileDescriptorProto.writeTo(outputStream);
                    }

                    Grasscutter.getLogger().info("Descriptor written to " + outputPath);
                } catch (NoClassDefFoundError | NoSuchMethodException e) {
                    Grasscutter.getLogger().warn("Skipping class " + clazz.getSimpleName() + " due to error: " + e.getMessage());
                } catch (Exception e) {
                    Grasscutter.getLogger().error("Failed to write descriptor for " + clazz.getSimpleName(), e);
                }
            }
        } catch (Exception e) {
            Grasscutter.getLogger().error("Failed to write descriptors.", e);
        }
    }
}