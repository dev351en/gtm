package com.sdcraft.clienthud;

import java.nio.charset.StandardCharsets;
import java.util.function.Function;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.network.codec.StreamCodec;
import net.minecraft.network.protocol.common.custom.CustomPacketPayload;
import net.minecraft.resources.Identifier;

/** Paper plugin-message bytes are raw UTF-8 JSON, without a Java UTF prefix. */
public final class HudPayloads {
    private HudPayloads() {}
    public record Hello(String json) implements CustomPacketPayload {
        public static final Type<Hello> TYPE=new Type<>(Identifier.fromNamespaceAndPath("gtm","hud_hello"));
        public static final StreamCodec<FriendlyByteBuf,Hello> CODEC=codec(Hello::new,Hello::json);
        public Type<Hello> type(){return TYPE;}
    }
    public record State(String json) implements CustomPacketPayload {
        public static final Type<State> TYPE=new Type<>(Identifier.fromNamespaceAndPath("gtm","hud_state"));
        public static final StreamCodec<FriendlyByteBuf,State> CODEC=codec(State::new,State::json);
        public Type<State> type(){return TYPE;}
    }
    public record Action(String json) implements CustomPacketPayload {
        public static final Type<Action> TYPE=new Type<>(Identifier.fromNamespaceAndPath("gtm","hud_action"));
        public static final StreamCodec<FriendlyByteBuf,Action> CODEC=codec(Action::new,Action::json);
        public Type<Action> type(){return TYPE;}
    }
    private static <T> StreamCodec<FriendlyByteBuf,T> codec(Function<String,T> create,Function<T,String> data) {
        return StreamCodec.of((buffer,payload)->{
            byte[] bytes=data.apply(payload).getBytes(StandardCharsets.UTF_8);
            if(bytes.length>HudState.MAX_BYTES)throw new IllegalArgumentException("HUD message exceeds bound");
            buffer.writeBytes(bytes);
        },buffer->{
            int size=buffer.readableBytes();
            if(size>HudState.MAX_BYTES)throw new IllegalArgumentException("HUD message exceeds bound");
            byte[] bytes=new byte[size];buffer.readBytes(bytes);
            return create.apply(new String(bytes,StandardCharsets.UTF_8));
        });
    }
}
