import { createAvatar } from '@dicebear/core';
import { funEmoji } from '@dicebear/collection';

const cache = new Map();

export function getAvatarDataUri(seed) {
  const key = String(seed || 'anon');
  if (cache.has(key)) return cache.get(key);
  const uri = createAvatar(funEmoji, { seed: key, size: 48 }).toDataUri();
  cache.set(key, uri);
  return uri;
}
