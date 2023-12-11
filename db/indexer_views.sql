/* Limit blocks select to one week to ensure fast query response */
drop view v_recent_blocks cascade;
CREATE VIEW public.v_recent_blocks as
SELECT
    blocks.workchain,
    blocks.shard,
    blocks.seqno,
    blocks.root_hash,
    blocks.file_hash,
    blocks.masterchain_block_id,
    block_headers.*,
    TO_TIMESTAMP(block_headers.gen_utime) as gen_ts
FROM
    blocks,
    block_headers
WHERE
        blocks.block_id = block_headers.block_id
  AND block_headers.gen_utime > (EXTRACT(EPOCH FROM NOW()) - 86400)::BIGINT;


drop view v_week_blocks cascade;
CREATE VIEW public.v_week_blocks as
SELECT
    blocks.workchain,
    blocks.shard,
    blocks.seqno,
    blocks.root_hash,
    blocks.file_hash,
    blocks.masterchain_block_id,
    block_headers.*,
    TO_TIMESTAMP(block_headers.gen_utime) as gen_ts
FROM
    blocks,
    block_headers
WHERE
        blocks.block_id = block_headers.block_id
  AND block_headers.gen_utime > (EXTRACT(EPOCH FROM NOW()) - 604800)::BIGINT;


drop view v_recent_blocks_latency cascade;
CREATE VIEW public.v_recent_blocks_latency as
WITH tmp_data as (SELECT
                      v_recent_blocks.*,
                      v_recent_blocks.gen_utime - LAG(v_recent_blocks.gen_utime)
                                                  OVER (
                                                      PARTITION BY
                                                          v_recent_blocks.workchain
                                                      ORDER BY
                                                          v_recent_blocks.seqno
                                                      )
                          AS "latency"
                  FROM
                      v_recent_blocks)
SELECT * from tmp_data where latency is not null;
;

drop view v_week_blocks_latency cascade;
CREATE VIEW public.v_week_blocks_latency as
WITH tmp_data as (SELECT
                      v_week_blocks.*,
                      v_week_blocks.gen_utime - LAG(v_week_blocks.gen_utime)
                                                  OVER (
                                                      PARTITION BY
                                                          v_week_blocks.workchain
                                                      ORDER BY
                                                          v_week_blocks.seqno
                                                      )
                          AS "latency"
                  FROM
                      v_week_blocks)
SELECT * from tmp_data where latency is not null;
;


drop view v_recent_blocks_crosschain_latency cascade;
CREATE VIEW public.v_recent_blocks_crosschain_latency as
WITH tmp_mc_blocks as (
    SELECT
        *
    FROM
        v_recent_blocks
    WHERE
            workchain = -1
)
SELECT
    v_recent_blocks.*,
    tmp_mc_blocks.gen_utime - v_recent_blocks.gen_utime as "crosschain_latency"
FROM
    v_recent_blocks,
    tmp_mc_blocks
WHERE
        v_recent_blocks.workchain >= 0
  AND v_recent_blocks.masterchain_block_id = tmp_mc_blocks.block_id
;

drop view v_recent_blocks_crosschain_statistics;
CREATE VIEW public.v_recent_blocks_crosschain_statistics as
WITH tmp_data as (
    SELECT
        v_recent_blocks.masterchain_block_id,
        min(v_recent_blocks.gen_utime) as gen_utime_min,
        round(avg(v_recent_blocks.gen_utime)) as gen_utime_avg,
        max(v_recent_blocks.gen_utime) as gen_utime_max,
        count(v_recent_blocks.gen_utime) as wc_block_load
    FROM
        v_recent_blocks
    WHERE
            v_recent_blocks.workchain >= 0
    GROUP BY
        v_recent_blocks.masterchain_block_id
)
SELECT
    v_recent_blocks.*,
    v_recent_blocks.gen_utime - tmp_data.gen_utime_min as children_latency_max,
    v_recent_blocks.gen_utime - tmp_data.gen_utime_avg as children_latency_avg,
    v_recent_blocks.gen_utime - tmp_data.gen_utime_max as children_latency_min,
    tmp_data.wc_block_load as children_count
FROM
    v_recent_blocks,
    tmp_data
WHERE
        v_recent_blocks.workchain = -1
  AND tmp_data.masterchain_block_id = v_recent_blocks.block_id
;

