import { OPENAI_API_BASE_URL, WEBUI_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';

export const getOpenAIConfig = async (token: string = '') => {
	let error = null;

	const res = await fetch(`${OPENAI_API_BASE_URL}/config`, {
		method: 'GET',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		}
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			if ('detail' in err) {
				error = err.detail;
			} else {
				error = 'Server connection failed';
			}
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

type OpenAIConfig = {
	ENABLE_OPENAI_API: boolean;
	OPENAI_API_BASE_URLS: string[];
	OPENAI_API_KEYS: string[];
	OPENAI_API_CONFIGS: object;
};

const dedupe = (values: string[]) => Array.from(new Set(values.filter(Boolean)));

const joinUrlPath = (baseUrl: string, path: string) => {
	const base = baseUrl.trim().replace(/\/$/, '');
	if (!path) return base;
	if (path.startsWith('http://') || path.startsWith('https://')) return path.replace(/\/$/, '');
	return `${base}/${path.replace(/^\//, '')}`;
};

const isOpenAIVersionedBasePath = (path: string) =>
	/(\/v1|\/v1beta|\/openai\/v1|\/v1beta\/openai|\/ml\/gateway\/v1|\/v2\/ext\/openai\/v1|\/compatible-mode\/v1|\/api\/paas\/v4|\/api\/v1|\/inference\/v1)$/.test(
		path.replace(/\/$/, '')
	);

const getProviderHint = (url: string) => {
	try {
		const hostname = new URL(url).hostname.toLowerCase();
		if (hostname.includes('generativelanguage.googleapis.com')) return 'gemini';
		if (hostname.includes('api.anthropic.com')) return 'anthropic';
		if (hostname.includes('openrouter.ai')) return 'openrouter';
		if (hostname.includes('groq.com')) return 'groq';
		if (hostname.includes('dashscope.aliyuncs.com') || hostname.includes('bailian.aliyuncs.com'))
			return 'ali';
		if (hostname.includes('bigmodel.cn') || hostname.endsWith('z.ai')) return 'zai';
		if (hostname.includes('fireworks.ai')) return 'fireworks';
		if (hostname.includes('perplexity.ai')) return 'perplexity';
		return '';
	} catch {
		return '';
	}
};

const getOpenAIEndpointUrl = (url: string, endpoint: string) => {
	const base = url.trim().replace(/\/$/, '');
	if (!base) return joinUrlPath(base, endpoint);

	try {
		const parsed = new URL(base);
		let path = parsed.pathname.replace(/\/$/, '');
		const provider = getProviderHint(base);

		if (path.endsWith(`/${endpoint}`)) return base;

		if (endpoint === 'chat/completions' && path.endsWith('/responses')) {
			path = path.replace(/\/responses$/, '');
			parsed.pathname = path;
			return joinUrlPath(parsed.toString().replace(/\/$/, ''), endpoint);
		}

		if (endpoint === 'responses' && path.endsWith('/chat/completions')) {
			path = path.replace(/\/chat\/completions$/, '');
			parsed.pathname = path;
			return joinUrlPath(parsed.toString().replace(/\/$/, ''), endpoint);
		}

		if (path.endsWith('/api') && parsed.origin === WEBUI_BASE_URL) {
			return joinUrlPath(base, endpoint);
		}

		if (isOpenAIVersionedBasePath(path)) return joinUrlPath(base, endpoint);

		if (provider === 'openrouter') return joinUrlPath(base, `/api/v1/${endpoint}`);
		if (provider === 'groq') return joinUrlPath(base, `/openai/v1/${endpoint}`);
		if (provider === 'ali') return joinUrlPath(base, `/compatible-mode/v1/${endpoint}`);
		if (provider === 'zai') return joinUrlPath(base, `/api/paas/v4/${endpoint}`);
		if (provider === 'fireworks') return joinUrlPath(base, `/inference/v1/${endpoint}`);
		if (provider === 'perplexity') return joinUrlPath(base, endpoint);

		return joinUrlPath(base, `/v1/${endpoint}`);
	} catch {
		return joinUrlPath(base, endpoint);
	}
};

const isGeminiModelsUrl = (url: string) => {
	try {
		const parsed = new URL(url);
		return parsed.hostname.includes('generativelanguage.googleapis.com') || parsed.pathname.includes('/v1beta');
	} catch {
		return false;
	}
};

const getModelDiscoveryUrls = (url: string) => {
	const base = url.trim().replace(/\/$/, '');
	if (!base) return [];

	let path = '';
	let provider = '';
	try {
		const parsed = new URL(base);
		path = parsed.pathname.replace(/\/$/, '');
		provider = getProviderHint(base);
	} catch {
		path = '';
	}

	if (path.endsWith('/models')) return [base];

	if (isGeminiModelsUrl(base)) {
		return dedupe([
			path.endsWith('/v1beta') ? joinUrlPath(base, '/models') : joinUrlPath(base, '/v1beta/models'),
			joinUrlPath(base, '/models'),
			joinUrlPath(base, '/v1/models')
		]);
	}

	if (provider === 'openrouter') {
		return dedupe([
			joinUrlPath(base, '/api/v1/models'),
			joinUrlPath(base, '/models'),
			joinUrlPath(base, '/v1/models')
		]);
	}

	if (provider === 'groq') {
		return dedupe([
			joinUrlPath(base, '/openai/v1/models'),
			joinUrlPath(base, '/models'),
			joinUrlPath(base, '/v1/models')
		]);
	}

	if (provider === 'ali') {
		return dedupe([
			joinUrlPath(base, '/compatible-mode/v1/models'),
			joinUrlPath(base, '/models'),
			joinUrlPath(base, '/v1/models')
		]);
	}

	if (provider === 'zai') {
		return dedupe([
			joinUrlPath(base, '/api/paas/v4/models'),
			joinUrlPath(base, '/models'),
			joinUrlPath(base, '/v1/models')
		]);
	}

	if (provider === 'fireworks') {
		return dedupe([
			joinUrlPath(base, '/inference/v1/models'),
			joinUrlPath(base, '/models'),
			joinUrlPath(base, '/v1/models')
		]);
	}

	const urls = [joinUrlPath(base, '/models')];
	if (!isOpenAIVersionedBasePath(path)) {
		urls.push(
			joinUrlPath(base, '/v1/models'),
			joinUrlPath(base, '/openai/v1/models'),
			joinUrlPath(base, '/compatible-mode/v1/models'),
			joinUrlPath(base, '/api/paas/v4/models'),
			joinUrlPath(base, '/api/v1/models'),
			joinUrlPath(base, '/inference/v1/models')
		);
	}

	return dedupe(urls);
};

const normalizeModelListResponse = (response: any) => {
	const rawModels = Array.isArray(response)
		? response
		: Array.isArray(response?.data)
			? response.data
			: Array.isArray(response?.models)
				? response.models
				: null;

	if (!rawModels) return null;

	const data = rawModels
		.map((model) => {
			const id =
				typeof model === 'string'
					? model
					: (model?.id ?? model?.name ?? model?.model ?? model?.slug ?? '');
			const normalizedId = `${id}`.replace(/^models\//, '').trim();
			if (!normalizedId) return null;
			return typeof model === 'object'
				? { ...model, id: normalizedId, name: model?.name ?? normalizedId }
				: { id: normalizedId, name: normalizedId, object: 'model' };
		})
		.filter(Boolean);

	return {
		...(Array.isArray(response) ? {} : response),
		object: response?.object ?? 'list',
		data
	};
};

export const updateOpenAIConfig = async (token: string = '', config: OpenAIConfig) => {
	let error = null;

	const res = await fetch(`${OPENAI_API_BASE_URL}/config/update`, {
		method: 'POST',
		headers: {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(token && { authorization: `Bearer ${token}` })
		},
		body: JSON.stringify({
			...config
		})
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			console.error(err);
			if ('detail' in err) {
				error = err.detail;
			} else {
				error = 'Server connection failed';
			}
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const getOpenAIModelsDirect = async (url: string, key: string) => {
	let error = null;

	let res = null;
	for (const modelUrl of getModelDiscoveryUrls(url)) {
		const headers: Record<string, string> = {
			Accept: 'application/json',
			'Content-Type': 'application/json',
			...(key && { authorization: `Bearer ${key}` })
		};
		if (key && isGeminiModelsUrl(modelUrl)) {
			delete headers.authorization;
			headers['x-goog-api-key'] = key;
		}

		res = await fetch(modelUrl, {
			method: 'GET',
			headers
		})
			.then(async (res) => {
				if (!res.ok) throw await res.json();
				return normalizeModelListResponse(await res.json());
			})
			.catch((err) => {
				error = `OpenAI: ${err?.error?.message ?? 'Network Problem'}`;
				return null;
			});

		if (res) {
			error = null;
			break;
		}
	}

	if (error) {
		throw error;
	}

	return res ?? { object: 'list', data: [] };
};

export const getOpenAIModels = async (token: string, urlIdx?: number) => {
	let error = null;

	const res = await fetch(
		`${OPENAI_API_BASE_URL}/models${typeof urlIdx === 'number' ? `/${urlIdx}` : ''}`,
		{
			method: 'GET',
			headers: {
				Accept: 'application/json',
				'Content-Type': 'application/json',
				...(token && { authorization: `Bearer ${token}` })
			}
		}
	)
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = `OpenAI: ${err?.error?.message ?? 'Network Problem'}`;
			return [];
		});

	if (error) {
		throw error;
	}

	return res;
};

export const verifyOpenAIConnection = async (
	token: string = '',
	connection: dict = {},
	direct: boolean = false
) => {
	const { url, key, config } = connection;
	if (!url) {
		throw 'OpenAI: URL is required';
	}

	let error = null;
	let res = null;

	if (direct) {
		res = await getOpenAIModelsDirect(url, key).catch((err) => {
			error = `${err}`;
			return null;
		});

		if (error) {
			throw error;
		}
	} else {
		res = await fetch(`${OPENAI_API_BASE_URL}/verify`, {
			method: 'POST',
			headers: {
				Accept: 'application/json',
				Authorization: `Bearer ${token}`,
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				url,
				key,
				config
			})
		})
			.then(async (res) => {
				if (!res.ok) throw await res.json();
				return res.json();
			})
			.catch((err) => {
				error = `OpenAI: ${err?.error?.message ?? 'Network Problem'}`;
				return [];
			});

		if (error) {
			throw error;
		}
	}

	return res;
};

export const chatCompletion = async (
	token: string = '',
	body: object,
	url: string = `${WEBUI_BASE_URL}/api`
): Promise<[Response | null, AbortController]> => {
	const controller = new AbortController();
	let error = null;

	const res = await fetch(getOpenAIEndpointUrl(url, 'chat/completions'), {
		signal: controller.signal,
		method: 'POST',
		headers: {
			Authorization: `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify(body)
	}).catch((err) => {
		console.error(err);
		error = err;
		return null;
	});

	if (error) {
		throw error;
	}

	return [res, controller];
};

export const generateOpenAIChatCompletion = async (
	token: string = '',
	body: object,
	url: string = `${WEBUI_BASE_URL}/api`
) => {
	let error = null;

	const res = await fetch(getOpenAIEndpointUrl(url, 'chat/completions'), {
		method: 'POST',
		headers: {
			Authorization: `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		credentials: 'include',
		body: JSON.stringify(body)
	})
		.then(async (res) => {
			if (!res.ok) throw await res.json();
			return res.json();
		})
		.catch((err) => {
			error = err?.detail ?? err;
			return null;
		});

	if (error) {
		throw error;
	}

	return res;
};

export const synthesizeOpenAISpeech = async (
	token: string = '',
	speaker: string = 'alloy',
	text: string = '',
	model: string = 'tts-1'
) => {
	let error = null;

	const res = await fetch(`${OPENAI_API_BASE_URL}/audio/speech`, {
		method: 'POST',
		headers: {
			Authorization: `Bearer ${token}`,
			'Content-Type': 'application/json'
		},
		body: JSON.stringify({
			model: model,
			input: text,
			voice: speaker
		})
	}).catch((err) => {
		console.error(err);
		error = err;
		return null;
	});

	if (error) {
		throw error;
	}

	return res;
};
