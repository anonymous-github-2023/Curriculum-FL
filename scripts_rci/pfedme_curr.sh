#!/bin/sh

python3 ../main.py \
    --ntrials=3 \
    --seed=202207 \
    --rounds=100 \
    --num_users=100 \
    --frac=0.1 \
    --local_ep=10 \
    --local_bs=10 \
    --lr0=0.001 \
    --lr_sched_a=0.001 \
    --lr_sched_b=0.75 \
    --w_decay=5e-4 \
    --momentum=0.9 \
    --pfedme_lambd=15 \
    --pfedme_K=5 \
    --pfedme_eta=0.005 \
    --pfedme_beta=2.0 \
    --model='simple-cnn' \
    --dataset='cifar10' \
    --partition='noniid-#label2' \
    --partition_difficulty_dist='rand' \
    --num_partitions=400 \
    --ordering='rand' \
    --pacing_f='linear' \
    --pacing_a=0.8 \
    --pacing_b=0.2 \
    --client_ordering='rand' \
    --client_pacing_f='step' \
    --client_pacing_a=1.0 \
    --client_pacing_b=1.0 \
    --client_bs=10 \
    --exp_label='T2n' \
    --datadir='../data/' \
    --logdir='../save_results/' \
    --ptdir='../pretrain/' \
    --train_expert='False' \
    --log_clientnet='False' \
    --data_score_sample_p=0.01 \
    --client_score_sample_n=1 \
    --log_filename='client100_rand_step_1.0a_1.0b_data_rand_linear_0.8a_0.2b_gloss_p400' \
    --alg='pfedme_curr' \
    --beta=0.1 \
    --local_view=True  \
    --lg_scoring='G' \
    --noise=0 \
    --gpu=0 \
    --print_freq=10
