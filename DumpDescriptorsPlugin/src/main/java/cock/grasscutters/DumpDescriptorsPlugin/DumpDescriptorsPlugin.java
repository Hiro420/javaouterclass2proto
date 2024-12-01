package cock.grasscutters.DumpDescriptorsPlugin;

import emu.grasscutter.plugin.Plugin;
import emu.grasscutter.server.event.EventHandler;
import emu.grasscutter.server.event.HandlerPriority;
import emu.grasscutter.server.event.entity.EntityDamageEvent;

public final class DumpDescriptorsPlugin extends Plugin {
    private static DumpDescriptorsPlugin instance;
    public static DumpDescriptorsPlugin getInstance() {
        return instance;
    }
    @Override public void onLoad() {
        // Set the plugin instance.
        instance = this;
    }
    @Override public void onEnable() {
        // Register the command
        this.getHandle().registerCommand(new cock.grasscutters.DumpDescriptorsPlugin.commands.DumpDescriptorsCommand());

        // Log a plugin status message.
        this.getLogger().info("[DumpDescriptors] The plugin has been enabled.");
    }

    @Override public void onDisable() {
        // Log a plugin status message.
        this.getLogger().info("[DumpDescriptors] The plugin has been disabled");
    }
}